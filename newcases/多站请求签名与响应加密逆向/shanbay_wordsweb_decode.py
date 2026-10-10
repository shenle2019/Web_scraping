# -*- coding: utf-8 -*-
"""
Day21 练习案例 3/4 —— 扇贝 web.shanbay.com「响应自定义编码」逆向
============================================================================
【练习来源】Day21 课件「练习案例」base64 目标3：
    aHR0cHM6Ly93ZWIuc2hhbmJheS5jb20vd29yZHN3ZWIvIy93b3Jkcy10YWJsZQ==
    = https://web.shanbay.com/wordsweb/#/words-table
    （注：课件学习笔记中曾把 wordsweb 误记为 web.shanghai.com/wordsweb）

【逆向结论】（axios 响应拦截器 + 编码类 k / PRNG 类 / Trie 类源码级复刻）
    真实加密接口（需登录，取各课件样本验证）:
        GET https://apiv3.shanbay.com/wordsapp/user_material_books/{book}/learning/words/today_learning_items
    匿名接口（当前线上为明文，可用于演示数据获取）:
        GET https://apiv3.shanbay.com/wordsapp/material_books
              ?tag_id=mnvdu&page=1&ipp=10&book_type=0
    应答:  {"code":..., "data":"<自定义字符集编码密文>"}
    解码链（源码 E 函数 + k 类）:
      1. 校验: ((32*S(c0)+S(c1))*S(c2)+S(c3)) % 32 <= 1
               S(ch)= charCode>=65 ? ch-65 : ch-24
      2. seed: 以密文前 4 字符 charCode 初始化 MT19937 变种 PRNG
               （mat1=status[1], mat2=status[2], tmat=status[3]; init 7 轮; 预热 8 次）
      3. Trie: 用 PRNG 为标准 base64 全部 64 字符生成"别名"
               （A~J 每字符 1 个符号，K 起每字符 2 个符号；符号集
               O="ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"，冲突避让）
      4. 还原: 密文自 index=4 起沿 Trie 贪心最长匹配，还原标准 base64 串
               （"=" 直接透传）-> Base64.decode -> JSON.parse

【验证结果】
    - 离线样本：对课件真实密文样本（seed=5DEV, 43708 字符）解码成功，
      还原 base64 前缀 eyJpcHAiOjEwLCJwYWdlIjo0... -> JSON {ipp:10, page:4,
      total:50, objects:10}，与课件请求参数 page=4 完全吻合
    - 在线接口：material_books / tags 当前线上返回明文 JSON（可匿名获取）

【用法】
    python shanbay_wordsweb_decode.py            # 在线请求 material_books
    python shanbay_wordsweb_decode.py --sample   # 离线解码 output/shanbay_cipher_sample.txt

【合规声明】匿名、低频（每次运行仅 1 个请求）、仅用于学习验证解码算法，
           不批量采集、不绕过任何登录/风控，输出数据仅本地留存。
"""
import argparse
import base64
import json
import os

import requests

API_URL = "https://apiv3.shanbay.com/wordsapp/material_books"
O = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"                          # 符号集（32 字符）
STD_B64 = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
           "abcdefghijklmnopqrstuvwxyz0123456789+/")            # 标准 base64 字母表
COUNTS = [1, 2, 2, 2, 2, 2]                                     # x = [1,2,2,2,2,2]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

MASK = 0xFFFFFFFF


# ---------------------------------------------------------------------------
# 1) PRNG：JS 类 _ 的逐行复刻（b 位运算库语义：每步 >>>0 截断为 32 位无符号）
# ---------------------------------------------------------------------------
class Prng:
    def __init__(self):
        self.status = [0, 0, 0, 0]
        self.mat1 = 0
        self.mat2 = 0
        self.tmat = 0

    @staticmethod
    def mul(a, b):
        # b.mul(a,b) = ((a&0xFFFF0000)*b + (a&0xFFFF)*b) >>> 0
        return ((((a & 0xFFFF0000) * b) & MASK) + (((a & 0xFFFF) * b) & MASK)) & MASK

    def seed(self, s: str):
        for i in range(4):                       # y.loop(4, ...) 不足补 110
            self.status[i] = (ord(s[i]) if len(s) > i else 110) & MASK
        self.mat1, self.mat2, self.tmat = self.status[1], self.status[2], self.status[3]
        self.init()

    def init(self):
        for t in range(7):                       # y.loop(7, ...)
            idx = (t + 1) & 3
            v = (t + 1 + self.mul(1812433253,
                                  self.status[3 & t] ^ (self.status[3 & t] >> 30))) & MASK
            self.status[idx] = (self.status[idx] ^ v) & MASK
        if ((self.status[0] & 0x7FFFFFFF) == 0 and self.status[1] == 0
                and self.status[2] == 0 and self.status[3] == 0):
            self.status = [66, 65, 89, 83]       # "BAYS"
        for _ in range(8):                       # y.loop(8, nextState)
            self.next_state()

    def next_state(self):
        t = self.status[3]
        e = (self.status[0] & 0x7FFFFFFF) ^ (self.status[1] ^ self.status[2])
        e = (e ^ ((e << 1) & MASK)) & MASK
        t = (t ^ ((t >> 1) ^ e)) & MASK
        s1, s2 = self.status[1], self.status[2]
        self.status[0] = s1
        self.status[1] = s2
        self.status[2] = (e ^ ((t << 10) & MASK)) & MASK
        self.status[3] = t
        if t & 1:                                # b.and(-b.and(t,1), mat) 的等价形式
            self.status[1] = (self.status[1] ^ self.mat1) & MASK
            self.status[2] = (self.status[2] ^ self.mat2) & MASK

    def generate(self, e):
        self.next_state()
        t = self.status[3]
        n = (self.status[0] ^ (self.status[2] >> 8)) & MASK
        t = (t ^ n) & MASK
        if n & 1:
            t = (t ^ self.tmat) & MASK
        return t % e


# ---------------------------------------------------------------------------
# 2) Trie 节点（JS 类 w：char 默认 "."，children 为字典）
# ---------------------------------------------------------------------------
class TrieNode:
    def __init__(self):
        self.char = "."
        self.children = {}


# ---------------------------------------------------------------------------
# 3) 解码器（JS 类 k：init / addSymbol / decode）
# ---------------------------------------------------------------------------
class Decoder:
    def __init__(self):
        self.random = Prng()
        self.inter = {}
        self.head = TrieNode()

    def init(self, seed_str: str):
        self.random.seed(seed_str)
        for e in range(64):
            # parseInt((e+1)/11, 10) -> x 索引
            self.add_symbol(STD_B64[e], COUNTS[(e + 1) // 11])
        self.inter["="] = "="

    def add_symbol(self, ch, t):
        r = self.head
        o = ""
        for _ in range(t):
            e = O[self.random.generate(32)]
            while e in r.children and r.children[e].char != ".":
                e = O[self.random.generate(32)]
            o += e
            if e not in r.children:
                r.children[e] = TrieNode()
            r = r.children[e]
        r.char = ch
        self.inter[ch] = o
        return o

    def decode(self, s: str) -> str:
        out = []
        n = 4
        while n < len(s):
            if s[n] != "=":
                r = self.head
                while n < len(s) and s[n] in r.children:
                    r = r.children[s[n]]
                    n += 1
                out.append(r.char)
            else:
                out.append("=")
                n += 1
        return "".join(out)


def sb_decode(cipher: str):
    """复刻源码 E(data)：校验 -> 初始化解码器 -> 还原 base64 -> 解出原文"""
    def sch(ch):
        t = ord(ch)
        return t - 65 if t >= 65 else t - 65 + 41

    if len(cipher) < 4:
        return ""
    check = ((32 * sch(cipher[0]) + sch(cipher[1])) * sch(cipher[2]) + sch(cipher[3])) % 32
    if check > 1:
        return ""
    dec = Decoder()
    dec.init(cipher[:4])
    b64 = dec.decode(cipher)
    raw = base64.b64decode(b64 + "=" * (-len(b64) % 4))
    return json.loads(raw.decode("utf-8"))


def run_sample_mode(sample_path=None):
    """离线模式：解码课件真实密文样本（强验证）"""
    sample_path = sample_path or os.path.join(OUT_DIR, "shanbay_cipher_sample.txt")
    cipher = open(sample_path, encoding="utf-8").read().strip()
    print("=" * 72)
    print("[1] 载入密文样本: %s" % sample_path)
    print("    seed=%s  长度=%d" % (cipher[:4], len(cipher)))

    def sch(ch):
        t = ord(ch)
        return t - 65 if t >= 65 else t - 65 + 41

    check = ((32 * sch(cipher[0]) + sch(cipher[1])) * sch(cipher[2]) + sch(cipher[3])) % 32
    print("    版本头校验值 %d (<=1 通过)" % check)

    p = Prng()
    p.seed(cipher[:4])
    seq = [p.generate(32) for _ in range(10)]
    print("    PRNG 前 10 值: %s" % seq)

    dec = Decoder()
    dec.init(cipher[:4])
    b64 = dec.decode(cipher)
    print("\n[2] 还原标准 base64 前缀: %s" % b64[:64])

    data = sb_decode(cipher)
    objects = data.get("objects") if isinstance(data, dict) else None
    objects = objects or []
    words = [(it.get("vocab_with_senses") or {}).get("word") for it in objects]
    if isinstance(data, dict):
        print("\n[3] 解码成功: ipp=%s page=%s total=%s"
              % (data.get("ipp"), data.get("page"), data.get("total")))
    else:
        print("\n[3] 解码类型异常: %s" % type(data))
    print("    objects=%d 词表: %s" % (len(objects), words[:10]))

    result = {
        "target": "shanbay 自定义编码解码器 vs 真实密文样本（离线）",
        "sample_file": os.path.basename(sample_path),
        "seed": cipher[:4],
        "cipher_length": len(cipher),
        "check_value": check,
        "prng_first10": seq,
        "b64_prefix": b64[:64],
        "decoded": {k: data.get(k) for k in ("ipp", "page", "total")} if isinstance(data, dict) else None,
        "words": words,
        "verified": bool(objects),
    }
    fp = os.path.join(OUT_DIR, "shanbay_sample_result.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n[4] 验证结果已保存: %s" % fp)


def run_online_mode():
    """在线模式：请求匿名接口 material_books（当前线上为明文，演示数据获取）"""
    headers = {
        "User-Agent": UA,
        "Referer": "https://web.shanbay.com/",
        "Accept": "application/json",
    }
    params = {"tag_id": "mnvdu", "page": 1, "ipp": 10, "book_type": 0}
    print("=" * 72)
    print("[1] 请求接口 GET %s" % API_URL)
    resp = requests.get(API_URL, params=params, headers=headers, timeout=15)
    print("    HTTP %s  Content-Type: %s" % (resp.status_code,
                                             resp.headers.get("Content-Type", "")))
    body = resp.json()
    print("    应答顶层 keys: %s" % list(body.keys())[:8])

    enc = body.get("data")
    if not isinstance(enc, str):
        print("    该接口未返回密文（内容为明文 JSON，应服务端策略变更），直接展示数据")
        payload = body
    else:
        print("    密文样例: %s ...（长度 %d）" % (enc[:64], len(enc)))
        print("\n[2] 复刻解码链：seed=%s -> PRNG -> Trie 别名 -> 标准 base64 -> JSON" % enc[:4])
        payload = sb_decode(enc)

    objects = []
    if isinstance(payload, dict):
        objects = payload.get("objects") or payload.get("list") or []
    print("\n[3] 明文 keys=%s objects=%d 条"
          % (list(payload.keys()) if isinstance(payload, dict) else "-", len(objects)))
    for i, it in enumerate(objects[:5], 1):
        name = (it.get("name") or it.get("title") or "") if isinstance(it, dict) else str(it)
        print("    %d. %s" % (i, name[:50]))

    result = {
        "target": "web.shanbay.com/wordsweb / apiv3.shanbay.com wordsapp/material_books",
        "cipher_sample": enc[:120] if isinstance(enc, str) else None,
        "http_status": resp.status_code,
        "encrypted": isinstance(enc, str),
        "verified": bool(objects),
        "decoded_keys": list(payload.keys()) if isinstance(payload, dict) else None,
        "object_count": len(objects),
        "sample": objects[:5],
    }
    fp = os.path.join(OUT_DIR, "shanbay_wordsweb_result.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n[4] 验证结果已保存: %s" % fp)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="离线解码课件密文样本（强验证）")
    ap.add_argument("--sample-file", default=None, help="自定义样本文件路径")
    args = ap.parse_args()
    if args.sample:
        run_sample_mode(args.sample_file)
    else:
        run_online_mode()


if __name__ == "__main__":
    main()
