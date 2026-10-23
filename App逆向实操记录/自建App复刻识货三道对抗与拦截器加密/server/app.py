# -*- coding: utf-8 -*-
"""本地验证服务端：复刻课件 day15 识货 App 的接口形态。

仅限学习研究，禁止商用。
本服务只监听局域网，数据全部为本地虚构商品，不连接任何第三方线上接口。

复刻的接口：
  1. GET  /app/version                                     版本检查（触发强制更新弹窗）
  2. POST /daga/search/goods/v1                            老版本搜索：明文、免请求头
  3. POST /v3/sh-api/daga/search/goods/v1                  新版本搜索：缺风控头返回 status=457
  4. GET  /v4/services/sh-goodsapi/app_swoole_shoe/preload/single
                                                           老版本详情：密文进密文出、明文进明文出，多调几次要验证码
  5. GET  /v4/services/sh-goodsapi/public/detail           新版本详情：明文、免头、免验证码
  6. GET  /app/ping                                        代理对照请求
  7. GET  /app/reset                                       重置验证码计数（便于重复验证）

配套的安卓 App 见 ../android，Frida 脚本见 ../frida。
"""
import base64
import json
import time

from flask import Flask, jsonify, request
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

APP = Flask(__name__)

# 拦截器里用的对称密钥，两边写死（复刻课件里"密钥藏在 so 里"的形态）
AES_KEY = b"shihuo-repl-key!"
LATEST_VERSION = "7.73.0"

# 虚构商品库
GOODS = [
    {"goods_id": "379112", "title": "Nike Air Zoom 篮球鞋", "price": "899", "shop": "识货优选旗舰店", "brand": "Nike"},
    {"goods_id": "1488642", "title": "李宁 韦德之道 10", "price": "1099", "shop": "李宁官方旗舰店", "brand": "李宁"},
    {"goods_id": "2129916", "title": "Spalding 斯伯丁 74-602Y 篮球", "price": "169", "shop": "斯伯丁运动专营店", "brand": "Spalding"},
    {"goods_id": "1110460", "title": "阿迪达斯 猎鹰 足球鞋", "price": "759", "shop": "阿迪达斯官方旗舰店", "brand": "Adidas"},
    {"goods_id": "520013", "title": "YONEX 尤尼克斯 弓箭11 球拍", "price": "1280", "shop": "尤尼克斯羽毛球馆", "brand": "YONEX"},
    {"goods_id": "660027", "title": "Wilson 威尔胜 网球拍 Pro Staff", "price": "1580", "shop": "威尔胜网球装备", "brand": "Wilson"},
]

_state = {"old_detail_calls": 0}
CAPTCHA_ANSWER = "8888"
CAPTCHA_THRESHOLD = 3


def _aes_encrypt(plain_text):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    data = cipher.encrypt(pad(plain_text.encode("utf-8"), 16))
    return base64.b64encode(data).decode("ascii")


def _aes_decrypt(cipher_text):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    data = cipher.decrypt(base64.b64decode(cipher_text))
    return unpad(data, 16).decode("utf-8")


def _find_goods(goods_id):
    for item in GOODS:
        if item["goods_id"] == goods_id:
            return dict(item)
    return None


def _log(tag):
    print("[%s] %s %s ip=%s ua=%s" % (
        time.strftime("%H:%M:%S"), request.method, request.full_path.rstrip("?"),
        request.remote_addr, request.headers.get("user-agent", "-")), flush=True)
    if tag:
        print("    -> %s" % tag, flush=True)


@APP.route("/app/version")
def app_version():
    _log("版本检查，强制更新")
    return jsonify({
        "code": 0,
        "data": {
            "latest": LATEST_VERSION,
            "min_supported": LATEST_VERSION,
            "force": True,
            "desc": "当前版本已停止维护，请升级后继续使用",
        },
    })


@APP.route("/daga/search/goods/v1", methods=["POST"])
def search_old():
    body = request.get_json(silent=True) or {}
    keyword = (body.get("keywords") or "").strip()
    page_size = int(body.get("pageSize") or 20)
    result = [g for g in GOODS if not keyword or keyword in g["title"] or keyword in g["brand"]]
    _log("老接口搜索 keyword=%s 命中=%d 条（无需请求头）" % (keyword, len(result)))
    return jsonify({
        "status": 0,
        "data": {"list": result[:page_size], "total": len(result), "page": body.get("page", "1")},
    })


@APP.route("/v3/sh-api/daga/search/goods/v1", methods=["POST"])
def search_new():
    sign = request.headers.get("sh-sign")
    token = request.headers.get("sh-token")
    if not sign or not token:
        _log("新接口搜索缺风控头，返回 457")
        return jsonify({"status": 457, "msg": "请检查是否使用了代理或VPN哦"})
    body = request.get_json(silent=True) or {}
    keyword = (body.get("keywords") or "").strip()
    result = [g for g in GOODS if not keyword or keyword in g["title"] or keyword in g["brand"]]
    _log("新接口搜索带齐风控头 sh-sign=%s 命中=%d 条" % (sign, len(result)))
    return jsonify({
        "status": 0,
        "data": {"list": result, "total": len(result), "page": body.get("page", "1")},
    })


@APP.route("/v4/services/sh-goodsapi/app_swoole_shoe/preload/single")
def detail_old():
    # 密文分支：data 参数是 Base64(AES(json))，原样加密回去
    if request.args.get("data"):
        try:
            plain = _aes_decrypt(request.args["data"])
            goods_id = (json.loads(plain) or {}).get("goods_id", "")
        except Exception as exc:  # noqa: BLE001
            _log("密文解密失败：%s" % exc)
            return jsonify({"status": 400, "msg": "bad data"})
        goods = _find_goods(goods_id)
        if not goods:
            return jsonify({"status": 404, "msg": "goods not found"})
        encrypted = _aes_encrypt(json.dumps({"status": 0, "data": goods, "code": 0}, ensure_ascii=False))
        _log("老详情密文进密文出 goods_id=%s" % goods_id)
        return jsonify({"status": 0, "dwlength": len(encrypted), "data": encrypted, "code": 0})

    # 明文分支：goods_id 直接查，但要过验证码
    goods_id = request.args.get("goods_id", "")
    captcha = request.args.get("captcha", "")
    _state["old_detail_calls"] += 1
    if _state["old_detail_calls"] > CAPTCHA_THRESHOLD and captcha != CAPTCHA_ANSWER:
        _log("老详情明文第 %d 次调用，触发图片验证码" % _state["old_detail_calls"])
        return jsonify({
            "status": 428,
            "msg": "请输入图片验证码后继续访问",
            "captcha_url": "/captcha",
            "hint": "本地演示固定验证码为 %s，带上 captcha 参数即可" % CAPTCHA_ANSWER,
        })
    goods = _find_goods(goods_id)
    if not goods:
        return jsonify({"status": 404, "msg": "goods not found"})
    _log("老详情明文进明文出 goods_id=%s（第 %d 次）" % (goods_id, _state["old_detail_calls"]))
    return jsonify({"status": 0, "data": goods, "code": 0})


@APP.route("/v4/services/sh-goodsapi/public/detail")
def detail_new():
    goods_id = request.args.get("goods_id", "")
    goods = _find_goods(goods_id)
    if not goods:
        return jsonify({"status": 404, "msg": "goods not found"})
    _log("新详情明文返回 goods_id=%s（免头、免验证码）" % goods_id)
    return jsonify({"status": 0, "data": goods, "code": 0})


@APP.route("/app/ping")
def ping():
    _log("代理对照请求")
    return jsonify({"code": 0, "msg": "pong", "server_time": int(time.time())})


@APP.route("/app/reset")
def reset():
    _state["old_detail_calls"] = 0
    return jsonify({"code": 0, "msg": "captcha counter reset"})


if __name__ == "__main__":
    print("本地验证服务启动：http://0.0.0.0:8000", flush=True)
    print("AES key = %s，验证码 = %s，老详情第 %d 次起要求验证码" % (
        AES_KEY.decode(), CAPTCHA_ANSWER, CAPTCHA_THRESHOLD + 1), flush=True)
    APP.run(host="0.0.0.0", port=8000, threaded=True)
