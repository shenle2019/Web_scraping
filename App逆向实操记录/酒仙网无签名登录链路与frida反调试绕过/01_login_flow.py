# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

酒仙网 v9.1.13 登录 + 预约链路复刻（本地 mock 版，不碰真站）。

课件结论：这几个接口没有签名，appKey / deviceIdentify / pushToken 都可以去掉，
真正卡人的只有"图形验证码 -> 短信验证码 -> token"这三步。本脚本完整跑一遍：
  1) 取图形验证码 -> ddddocr 识别 -> 提交校验（失败重试）
  2) 取模拟短信验证码 -> 短信登录拿 token
  3) 用户名密码登录拿 token（两条登录路径都验一遍）
  4) 用 token 调预约接口，再调一次验证"重复预约"错误码

用法：python 01_login_flow.py [--base http://127.0.0.1:8008] [--out 结果日志]
"""
import argparse
import base64
import io
import os
import sys
import time
import uuid

import requests

try:
    import ddddocr
except ImportError:
    ddddocr = None

HEADERS = {"secure": "false", "user-agent": "okhttp/3.14.9"}


def common_params(mobile, device_identify):
    return {
        "appKey": device_identify,
        "appVersion": "9.1.13",
        "areaId": "2707",
        "channelCode": "0",
        "cpsId": "tencent",
        "deviceIdentify": device_identify,
        "deviceType": "ANDROID",
        "deviceTypeExtra": "0",
        "equipmentType": "Pixel 2",
        "mobile": mobile,
        "netEnv": "wifi",
        "screenReslolution": "1080x1920",
        "supportWebp": "1",
        "sysVersion": "11",
    }


def fetch_and_check_captcha(base, mobile, device_identify, retries=10):
    ocr = ddddocr.DdddOcr(show_ad=False) if ddddocr else None
    for i in range(1, retries + 1):
        params = common_params(mobile, device_identify)
        params["type"] = "4"
        res = requests.get(base + "/messages/graphCode.htm", params=params, headers=HEADERS, timeout=5)
        img = base64.b64decode(res.json()["result"]["imgCode"])
        if ocr is None:
            raise SystemExit("未安装 ddddocr：pip install ddddocr")
        code = ocr.classification(img)
        check = common_params(mobile, device_identify)
        check.update({"code": code, "type": "1"})
        r2 = requests.get(base + "/messages/mobileCode.htm", params=check, headers=HEADERS, timeout=5)
        ok = r2.json().get("success") == "1"
        print("[captcha] 第%d次 OCR=%r -> %s" % (i, code, "通过" if ok else r2.json().get("errMsg")))
        if ok:
            return code
        time.sleep(0.5)
    raise SystemExit("图形验证码连续 %d 次识别失败" % retries)


def login_by_sms(base, mobile, device_identify):
    sms = requests.get(base + "/__mock/sms", params={"mobile": mobile}, timeout=5).json()["result"]["code"]
    data = common_params(mobile, device_identify)
    data.pop("mobile")
    data.update({"mobile": mobile, "verifyCode": sms})
    res = requests.post(base + "/user/loginMobileFast.htm", data=data, timeout=5)
    body = res.json()
    print("[sms-login] HTTP %d %s" % (res.status_code, body.get("errMsg") or "ok"))
    if body.get("success") != "1":
        raise SystemExit("短信登录失败: %s" % body)
    return body["result"]["userInfo"]["token"]


def login_by_pwd(base, mobile, password, device_identify):
    data = common_params(mobile, device_identify)
    data.pop("mobile")
    data.update({"userName": mobile, "passWord": password})
    res = requests.post(base + "/user/loginUserNamePassWd.htm", data=data, timeout=5)
    body = res.json()
    print("[pwd-login] HTTP %d %s" % (res.status_code, body.get("errMsg") or "ok"))
    if body.get("success") != "1":
        raise SystemExit("密码登录失败: %s" % body)
    return body["result"]["userInfo"]["token"]


def pre_reservation(base, token, device_identify, act_id="2168", product_id="626626"):
    params = common_params("", device_identify)
    params.pop("mobile")
    params.update({"actId": act_id, "channel": "1", "productId": product_id, "token": token})
    res = requests.get(base + "/reservation/preReservation.htm", params=params, timeout=5)
    body = res.json()
    print("[reservation] HTTP %d success=%s %s" % (res.status_code, body.get("success"), body.get("errMsg") or ""))
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8008")
    ap.add_argument("--mobile", default="15131255555")
    ap.add_argument("--password", default="123456")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    device_identify = str(uuid.uuid4())
    logs = []

    def log(line):
        print(line)
        logs.append(line)

    log("base=%s deviceIdentify=%s" % (args.base, device_identify))
    log("== 1. 图形验证码 + OCR ==")
    fetch_and_check_captcha(args.base, args.mobile, device_identify)
    log("== 2. 短信验证码登录 ==")
    token = login_by_sms(args.base, args.mobile, device_identify)
    log("token=%s" % token)
    log("== 3. 用户名密码登录 ==")
    token2 = login_by_pwd(args.base, args.mobile, args.password, device_identify)
    log("token2=%s" % token2)
    log("== 4. 预约（两次，第二次应返回重复预约）==")
    first = pre_reservation(args.base, token, device_identify)
    second = pre_reservation(args.base, token, device_identify)
    log("first=%s" % first)
    log("second=%s" % second)
    ok = first.get("success") == "1" and second.get("errCode") == "1200601"
    log("结论：%s" % ("PASS 全部链路跑通" if ok else "FAIL 链路未跑通"))

    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(logs) + "\n")
        print("已写入 %s" % os.path.abspath(args.out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
