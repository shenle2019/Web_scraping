# -*- coding: utf-8 -*-
"""案例3 企名片：Python 端复刻 3DES-ECB 解密，与 Node 原版 JS 结果对比验证"""
import base64
import json

from Crypto.Cipher import DES3

# 1. 从样本 JSON 提取加密串（json 解析自动处理 \\/ 转义）
sample = json.load(open("分析素材/vipapi_sample.json", encoding="utf-8"))
enc = sample["encrypt_data"]
print("加密串长度:", len(enc))

# 2. pycryptodome 3DES-ECB 解密（与 JS kt(key, data, 0, 0, iv, 1) 等价）
key = b"5e5062e82f15fe4ca9d24bc5"  # 24 bytes -> 3DES（老版 vipapi 密钥）
ct = base64.b64decode(enc)
print("密文字节数:", len(ct), "| 8字节对齐:", len(ct) % 8 == 0)

cipher = DES3.new(key, DES3.MODE_ECB)
pt = cipher.decrypt(ct)

# 3. 去 PKCS7 padding（与 JS w===1 分支一致：取最后字节为 padding 长度）
pad = pt[-1]
print("末尾 padding 字节值:", pad)
if 0 < pad <= 8:
    pt_clean = pt[:-pad]
else:
    pt_clean = pt

text = pt_clean.decode("utf-8", errors="replace")
print("\n解密结果前 400 字符:")
print(text[:400])

# 4. 与 Node 原版 JS 解密结果对比
try:
    node_text = open("分析素材/vipapi_decrypted.json", encoding="utf-8").read()
    print("\n=== 对比 Node 原版 JS 解密结果 ===")
    print("完全一致:", node_text == text)
    if node_text != text:
        print("Node 长度:", len(node_text), "| Python 长度:", len(text))
        print("Node 前 200:", repr(node_text[:200]))
        print("Python 前 200:", repr(text[:200]))
except FileNotFoundError:
    print("(Node 结果文件不存在，跳过对比)")

# 5. JSON 解析 + 保存
print("\n=== Python 解密结果 ===")
try:
    data = json.loads(text)
    print("JSON 解析成功! 数据条数:", len(data), "| 首条键:", list(data[0].keys()) if data else "-")
    with open("分析素材/vipapi_decrypted_python.json", "w", encoding="utf-8") as f:
        f.write(text)
    print("已保存 分析素材/vipapi_decrypted_python.json")
    print("首条内容:", json.dumps(data[0], ensure_ascii=False)[:300])
except Exception as e:
    print("JSON 解析失败:", e)
