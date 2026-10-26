# -*- coding: utf-8 -*-
"""Python 侧独立复刻（与 App 同算法的第二实现，用于交叉验证）。

仅限学习研究，禁止商用。只连接本机 mock server，不访问任何线上服务。

用法:
    python client_replica.py                # 发一轮 click + 心跳开始/结束
    python client_replica.py --base http://127.0.0.1:8899
"""
import argparse
import base64
import hashlib
import json
import random
import string
import time
import urllib.parse

import requests
from Crypto.Cipher import AES

SHA256_SALT = "9cafa6466a028bfb"
AES_KEY = b"fd6b639dbcff0c2a1b03b389ec763c4b"
AES_IV = b"77b07a672d57d64c"
MD5_SALTS = ["560c52cc", "d288fed0", "45859ed1", "8bffd973"]

AID, CID, DURATION = 8848, 175882888, 600


def rand_hex(n):
    return "".join(random.choice("0123456789abcdef") for _ in range(n))


def pkcs5_pad(data):
    """Java 的 AES/CBC/PKCS5Padding 会自己补块，pycryptodome 需要手动补"""
    pad = 16 - len(data) % 16
    return data + bytes([pad]) * pad


def device_id(mac, bt="", bus="", sn=None):
    sn = sn or rand_hex(16).upper()
    raw = "%s|%s|%s|%s" % (mac, bt, bus, sn)
    data = bytearray(raw.encode())
    data[0] ^= len(data) & 0xFF
    for i in range(1, len(data)):
        data[i] ^= data[i - 1]
    return base64.b64encode(bytes(data)).decode().rstrip("=")


def buvid():
    uuid = rand_hex(32)
    m = hashlib.md5(uuid.encode()).hexdigest()
    return ("XW" + m[2] + m[12] + m[22] + m).upper()


def fp_checksum(s):
    limit = min(len(s) - 1, 62)
    total = 0
    for i in range(0, limit - 1, 2):
        total += int(s[i:i + 2], 16)
    return "%02x" % (total % 256)


def fingerprint(bv, model, band):
    str2 = (hashlib.md5((bv + model + band).encode()).hexdigest()
            + time.strftime("%Y%m%d%H%M%S")
            + rand_hex(16))
    return str2 + fp_checksum(str2)


def headers(profile):
    return {
        "Display-ID": "%s-%d-0" % (profile["buvid"], int(time.time() * 1000)),
        "Buvid": profile["buvid"],
        "User-Agent": ("BiliDroid/6.24.0.0 os/android model/%s mobi_app/android "
                       "build/6240300 channel/master innerVer/6240300 osVer/11 network/2"
                       % profile["model"]),
        "Device-ID": profile["device_id"],
        "fp_local": profile["fp_local"],
        "fp_remote": profile["fp_remote"],
        "session_id": profile["session_id"],
        "app-key": "android64",
    }


def build_profile():
    mac = rand_hex(12)
    bv = buvid()
    return {
        "mac": mac,
        "model": "Pixel 2",
        "band": "google",
        "device_id": device_id(mac),
        "buvid": bv,
        "session_id": rand_hex(8),
        "fp_local": fingerprint(bv, "Pixel 2", "google"),
        "fp_remote": fingerprint(bv, "Pixel 2", "google"),
    }


def click_body(profile, aid=AID, cid=CID, duration=DURATION):
    now = int(time.time() * 1000)
    params = {
        "aid": aid, "cid": cid, "part": 1, "mid": 0, "lv": 0,
        "ftime": now - 10000, "stime": now - 5000, "did": profile["device_id"],
        "type": 3, "sub_type": 0, "sid": 0, "epid": 0, "auto_play": 0,
        "build": 6240300, "mobi_app": "android",
        "spmid": "main.ugc-video-detail.0.0",
        "from_spmid": "main.ugc-video-detail.0.0",
        "video_duration": duration,
    }
    plain = "&".join("%s=%s" % (k, params[k]) for k in sorted(params))
    sign = hashlib.sha256((plain + SHA256_SALT).encode()).hexdigest()
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    body = cipher.encrypt(pkcs5_pad((plain + "&sign=" + sign).encode()))
    return body, sign


def heartbeat_session(profile):
    raw = profile["buvid"] + str(int(time.time() * 1000)) + str(random.randint(0, 999999))
    return hashlib.sha1(raw.encode()).hexdigest()


def heartbeat_body(profile, start_ts, end, session, aid=AID, cid=CID, duration=DURATION):
    now = int(time.time() * 1000)
    total = (now - start_ts) // 1000
    played = duration if end else 0
    paused = max(0, total - duration) if end else 0
    params = {
        "aid": aid, "cid": cid, "sid": 0, "epid": 0, "type": 3, "sub_type": 0,
        "quality": 32, "video_duration": duration,
        "played_time": played, "paused_time": paused,
        "total_time": total if end else 0,
        "actual_played_time": played,
        "last_play_progress_time": played,
        "max_play_progress_time": played,
        "start_ts": start_ts // 1000, "ts": now // 1000,
        "statistics": json.dumps({"autoplay": 1, "card_type": 0, "platform": "android"},
                                 separators=(",", ":")),
        "session": session,
    }
    plain = "&".join("%s=%s" % (k, urllib.parse.quote_plus(str(params[k])))
                     for k in sorted(params))
    sign = hashlib.md5((plain + "".join(MD5_SALTS)).encode()).hexdigest()
    return (plain + "&sign=" + sign).encode(), sign


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8899")
    args = ap.parse_args()

    profile = build_profile()
    print("[profile] buvid=%s" % profile["buvid"])
    print("[profile] device_id=%s" % profile["device_id"])
    print("[profile] fp_local=%s" % profile["fp_local"])

    body, sign = click_body(profile)
    print("[click] sign=%s cipher=%dB" % (sign, len(body)))
    r = requests.post(args.base + "/x/report/click/android2", data=body,
                      headers=dict(headers(profile),
                                   **{"Content-Type": "application/json; charset=utf-8"}),
                      timeout=10)
    print("[click] resp=%s" % r.text)
    click_ok = r.json().get("verified") is True

    start_ts = int(time.time() * 1000) - (DURATION + 5) * 1000
    session = heartbeat_session(profile)
    ok_all = click_ok
    for end in (False, True):
        body, sign = heartbeat_body(profile, start_ts, end, session)
        tag = "end" if end else "start"
        print("[heartbeat:%s] sign=%s" % (tag, sign))
        r = requests.post(args.base + "/x/report/heartbeat/mobile", data=body,
                          headers=dict(headers(profile),
                                       **{"Content-Type":
                                          "application/x-www-form-urlencoded; charset=utf-8"}),
                          timeout=10)
        print("[heartbeat:%s] resp=%s" % (tag, r.text))
        ok_all = ok_all and r.json().get("verified") is True
        time.sleep(1.2)

    print("[result] python_replica=%s" % ("PASS" if ok_all else "FAIL"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
