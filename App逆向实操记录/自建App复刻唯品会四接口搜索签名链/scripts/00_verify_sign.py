# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。

00_verify_sign.py —— 唯品会 v7.83.3 签名算法与课件 hook 样本对照验证
来源课件：E:\路飞学城\课件\APP逆向(12期)\day20-唯品会01、day21-唯品会02

背景：
  libkeyinfo.so 的 getByteHash 内部是带盐的双层 sha1（盐 + 内容 -> hex，
  再 盐 + hex -> hex），api_sign / vcspSign 均由此得出；
  esNav 的 edata 是 AES-CBC-PKCS5，key = md5(盐) 的 16 字节 digest，
  iv = 16 位随机 hex 字符串，edata = base64(iv_bytes + 密文)。

本脚本用课件里 hook 到的样本做纯算对照：
  1. device_reg 的 api_sign（课件 day20 3.3.3 的 hook 输出）
  2. getTokenByFP 的 vcspSign（课件 day20 4.4 的 hook 输出）
  3. generate_token 的 AES key（课件 day21 3.4.4 的 hook 输出）
  4. generate_token 的 edata 前段（课件 day21 3.8 的 hook 输出）
"""
import hashlib
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def sha1(data_string: str) -> str:
    h = hashlib.sha1()
    h.update(data_string.encode('utf-8'))
    return h.hexdigest()


def api_sign(ordered_string: str, salt: str) -> str:
    """libkeyinfo.so getByteHash 等价逻辑：盐 + 内容 做两次 sha1"""
    tmp = sha1(f"{salt}{ordered_string}")
    return sha1(f"{salt}{tmp}")


def main():
    ok = True

    # ---------- 1. device_reg 的 api_sign（课件 day20 3.3.3 样本） ----------
    ordered = (
        "app_name=achievo_ad&app_version=7.83.3&channel=oziq7dxw:::&device=Pixel 2 XL"
        "&device_token=a9d1a2b9-2a79-36fd-a8ca-cbe24c03979d&manufacturer=Google"
        "&os_version=30&regPlat=0&regid=null&rom=Dalvik/2.1.0 (Linux; U; Android 11; "
        "Pixel 2 XL Build/RP1A.201005.004.A1)&skey=6692c461c3810ab150c9a980d0c275ec"
        "&status=1&vipruid=&warehouse=VIP_SH"
    )
    salt = "aee4c425dbb2288b80c71347cc37d04b"
    got = api_sign(ordered, salt)
    expect = "f4f002d40e112a06ecdc04e54d5bf9c92c0477aa"  # 课件 hook 输出
    print("[1] device_reg api_sign")
    print("    计算:", got)
    print("    hook:", expect, "->", "一致" if got == expect else "不一致!!!")
    ok &= (got == expect)

    # 课件 3.3.3 里第一步 sha1 的中间值也对照一下
    mid = sha1(f"{salt}{ordered}")
    print("    中间:", mid, "->", "一致" if mid == "f5fb31c0c3081d18c3f15c193e6f0c3868ae8d14" else "不一致!!!")
    ok &= (mid == "f5fb31c0c3081d18c3f15c193e6f0c3868ae8d14")

    # ---------- 2. getTokenByFP 的 vcspSign（课件 day20 4.4 样本） ----------
    vcsp_salt = "da19a1b93059ff3609fc1ed2e04b0141"
    got = api_sign("vcspKey=4d9e524ad536c03ff203787cf0dfcd29", vcsp_salt)
    expect = "05a68135d2bfd322e3a22f95bbc25a24c777f387"  # 课件抓包固定值
    print("[2] getTokenByFP vcspSign")
    print("    计算:", got)
    print("    hook:", expect, "->", "一致" if got == expect else "不一致!!!")
    ok &= (got == expect)

    # ---------- 3. generate_token 的 AES key（课件 day21 3.4.4） ----------
    md5 = hashlib.md5()
    md5.update(b'aee4c425dbb2288b80c71347cc37d04b')
    key = md5.digest()
    print("[3] edata AES key = md5(盐)")
    print("    计算:", key.hex())
    print("    hook:", "cdd17ab29b84b32552ddcfbb4abf0225", "->",
          "一致" if key.hex() == "cdd17ab29b84b32552ddcfbb4abf0225" else "不一致!!!")
    ok &= (key.hex() == "cdd17ab29b84b32552ddcfbb4abf0225")

    # ---------- 4. generate_token 的 edata（课件 day21 3.8 样本） ----------
    plaintext = (
        "app_name=shop_android&app_version=7.83.3&client_type=android"
        "&dinfo=%7B%22ah1%22%3A%22%22%2C%22ah2%22%3A%22%22%2C%22ah3%22%3A%22%22%2C"
        "%22ah4%22%3A%22wifi%22%2C%22ah5%22%3A%221440_2712%22%2C%22ah6%22%3A1900800"
        "%2C%22ah7%22%3A8%2C%22ah8%22%3A3839954944%2C%22ah9%22%3A%22Pixel+2+XL%22%2C"
        "%22ah10%22%3A%22%22%2C%22ah11%22%3A%22%22%2C%22ah12%22%3A%22%22%2C%22ah13"
        "%22%3A%22%22%2C%22as1%22%3A%2211%22%2C%22as2%22%3A%22%22%2C%22as3%22%3A%22"
        "%22%2C%22as4%22%3A%22cff15d2b8c13bf22%22%2C%22as5%22%3A%22%22%2C%22as6%22%3A"
        "%22%22%2C%22as7%22%3A%2230%22%2C%22ac1%22%3A%22a9d1a2b9-2a79-36fd-a8ca-cbe2"
        "4c03979d%22%7D&mars_cid=a9d1a2b9-2a79-36fd-a8ca-cbe24c03979d&phone_model="
        "Pixel+2+XL&session_id=a9d1a2b9-2a79-36fd-a8ca-cbe24c03979d_shop_android_"
        "1692875431421&sys_version=30&vcspKey=4d9e524ad536c03ff203787cf0dfcd29"
        "&vcspToken=NGQ5ZTUyNGFkNTM2YzAzZmYyMDM3ODdjZjBkZmNkMjl8fHwxNjk1NDY3MzcxfHx8"
        ".4f176037624c6f9736751183730c2ba5"
    )
    iv = "b04c6ab2831713b9"  # 课件 3.8 hook 到的随机 iv
    aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv.encode('utf-8'))
    raw = pad(plaintext.encode('utf-8'), 16)
    enc = aes.encrypt(raw)
    edata = b64encode(iv.encode('utf-8') + enc).decode('utf-8')
    print("[4] edata = base64(iv + AES密文)")
    print("    计算前40:", edata[:40])
    print("    hook前40:", "YjA0YzZhYjI4MzE3MTNiOTUsSEev23EXFvfqid/eINn0", "->",
          "一致" if edata.startswith("YjA0YzZhYjI4MzE3MTNiOTUsSEev23EXFvfqid/eINn0") else "不一致!!!")
    # 更严格：比对密文前 16 字节 hex 与课件 AES密文前 32 hex
    print("    密文hex前32:", enc[:16].hex())
    print("    hook前32   :", "352c4847afdb711716f7ea89dfde20d9", "->",
          "一致" if enc[:16].hex() == "352c4847afdb711716f7ea89dfde20d9" else "不一致!!!")
    ok &= (enc[:16].hex() == "352c4847afdb711716f7ea89dfde20d9")

    print()
    print("全部对照:", "通过" if ok else "存在不一致")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
