# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
02_验证MD5.py
目标：验证车智赢 App 登录密码的加密算法。
      依据 jadx 反编译结果：
      - com.che168.autotradercloud.user.model.UserModel.loginByPassword()
          调用 param("pwd", SecurityUtil.encodeMD5(密码明文))
      - com.autohome.ahkit.utils.SecurityUtil.encodeMD5()
          为 MessageDigest.getInstance("MD5") + 小写十六进制输出
      本脚本用 hashlib 复算 MD5，与 Charles 抓包得到的 pwd 密文比对。
用法：python 02_验证MD5.py
"""
import hashlib

PLAINTEXT = "1111111"                              # 课件中测试账号的密码明文
CAPTURED_PWD = "7fa8282ad93047a4d6fe6111c93b308a"   # Charles 抓包得到的 pwd 密文
COURSE_EXPECTED = "7fa8282ad93047a4d6fe6111c93b308a"  # 课件给出的标准结果


def encode_md5(text: str) -> str:
    """复刻 SecurityUtil.encodeMD5：标准 MD5，输出小写十六进制"""
    return hashlib.md5(text.encode()).hexdigest()


def main() -> None:
    calc = encode_md5(PLAINTEXT)
    print("=" * 66)
    print(f"[明文] {PLAINTEXT}")
    print(f"[本地复算 MD5] {calc}")
    print(f"[Charles 抓包 pwd] {CAPTURED_PWD}")
    print(f"[课件标准结果]    {COURSE_EXPECTED}")
    print("-" * 66)
    ok = (calc == CAPTURED_PWD == COURSE_EXPECTED)
    verdict = "登录密码加密 = 标准 MD5(32位小写hex)，验证通过" if ok else "需排查"
    print(f"[结论] 三者{'一致' if ok else '不一致'} -> {verdict}")
    print("=" * 66)


if __name__ == "__main__":
    main()
