# -*- coding: utf-8 -*-
"""repl_case.py —— 复刻课件 day15 的最终结论：老搜索拿 goods_id + 新详情拿数据。

对应课件的"接口混用"思路：老接口免风控头但方便，新详情免头免验证码。
顺带把课件里的两个现象在本机服务端上复现出来：
  1. 新搜索不带 sh-sign / sh-token -> status=457（请检查是否使用了代理或VPN哦）
  2. 老详情密文进密文出：data=AES-ECB-Base64({"goods_id":...})，响应也是密文

仅访问本机 192.168.31.220:8000 的自建服务，低频调用，仅限学习研究，禁止商用。
用法：python repl_case.py [keyword]
"""
import base64
import json
import sys

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

BASE = "http://192.168.31.220:8000"
AES_KEY = b"shihuo-repl-key!"
UA_OLD = (
    "Android 11 {Z29vZ2xl} CPU_ABI arm64-v8a CPU_ABI2  HARDWARE taimen "
    "MODEL {UGl4ZWwgMiBYTA} network/WIFI shihuo/7.20.1 sc({holder},myapp) "
    "minVersion(15670) sh-dv-sign[v1|repl]"
)


def aes_encrypt(plain):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(pad(plain.encode("utf-8"), 16))).decode()


def aes_decrypt(b64_text):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return unpad(cipher.decrypt(base64.b64decode(b64_text)), 16).decode("utf-8")


def old_search(keyword):
    """老搜索：只需要一个写死 sh-dv-sign 的 UA，不用 sh-sign/sh-token。"""
    url = BASE + "/daga/search/goods/v1"
    params = {
        "minVersion": "15670", "clientCode": "{holder}", "v": "7.20.1",
        "channel": "myapp", "device": "Pixel 2 XL", "platform": "android",
        "timestamp": str(int(__import__("time").time() * 1000)),
    }
    body = {"keywords": keyword, "page": "1", "pageSize": "20"}
    resp = requests.post(url, params=params, json=body, headers={"user-agent": UA_OLD}, timeout=10)
    return resp.json()


def new_search_no_headers(keyword):
    """新搜索不带风控头，复现 457。"""
    url = BASE + "/v3/sh-api/daga/search/goods/v1"
    params = {"minVersion": "19612", "v": "7.73.0", "platform": "android"}
    body = {"keywords": keyword, "page": "1", "pageSize": "20"}
    resp = requests.post(url, params=params, json=body, timeout=10)
    return resp.json()


def new_detail(goods_id):
    """新详情：public/detail，免头、免验证码、明文。"""
    resp = requests.get(BASE + "/v4/services/sh-goodsapi/public/detail",
                        params={"goods_id": goods_id, "v": "7.73.0"}, timeout=10)
    return resp.json()


def old_detail_cipher(goods_id):
    """老详情密文分支：加密进、加密出。"""
    data = aes_encrypt(json.dumps({"goods_id": goods_id}, separators=(",", ":")))
    resp = requests.get(BASE + "/v4/services/sh-goodsapi/app_swoole_shoe/preload/single",
                        params={"data": data, "v": "7.20.1"}, timeout=10)
    payload = resp.json()
    return data, aes_decrypt(payload["data"]) if isinstance(payload.get("data"), str) else payload


def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else "篮球"
    result = {"keyword": keyword}

    print("[1] 老搜索（免风控头）")
    old = old_search(keyword)
    goods_list = (old.get("data") or {}).get("list") or []
    if not goods_list:
        print("    未命中，终止")
        return 1
    goods_id = goods_list[0]["goods_id"]
    result["old_search"] = {"status": old.get("status"), "goods_id": goods_id,
                            "title": goods_list[0].get("title")}
    print("    status=%s goods_id=%s title=%s" % (old.get("status"), goods_id, goods_list[0].get("title")))

    print("[2] 新搜索不带 sh-sign/sh-token")
    new_no_head = new_search_no_headers(keyword)
    result["new_search_without_headers"] = new_no_head
    print("    %s" % json.dumps(new_no_head, ensure_ascii=False))

    print("[3] 新详情（public/detail，明文免头）")
    detail = new_detail(goods_id)
    result["new_detail"] = detail.get("data")
    print("    %s" % json.dumps(detail.get("data"), ensure_ascii=False))

    print("[4] 老详情（密文进密文出）")
    cipher_in, plain_out = old_detail_cipher(goods_id)
    result["old_detail_cipher"] = {"data": cipher_in, "decrypted": plain_out}
    print("    data=%s" % cipher_in)
    print("    解密后=%s" % plain_out)

    with open("repl_result.json", "w", encoding="utf-8") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
    print("[ok] 结果已写入 repl_result.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
