# -*- coding: utf-8 -*-
"""提取 iconfont.570166c6.js 中的 kt/Tt 解密函数（括号配对法）"""
import re

js = open("分析素材/qmp_js/iconfont.570166c6.js", encoding="utf-8", errors="replace").read()


def extract_fn(src, name):
    start = src.find("function %s(" % name)
    if start < 0:
        return None, -1
    i = src.find("{", start)
    depth = 0
    j = i
    in_s = None
    while j < len(src):
        ch = src[j]
        if in_s:
            if ch == "\\":
                j += 2
                continue
            if ch == in_s:
                in_s = None
        else:
            if ch in ('"', "'"):
                in_s = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
        j += 1
    return src[start:j + 1], start


names = ["Tt", "kt"]
parts = []
for nm in names:
    fn, pos = extract_fn(js, nm)
    if fn:
        print("%s 函数: 位置 %d, 长度 %d" % (nm, pos, len(fn)))
        parts.append(fn)
    else:
        print("%s 函数未找到" % nm)

module = "\n".join(parts) + "\n"
open("分析素材/kt_module.js", "w", encoding="utf-8").write(module)
print("模块已保存 分析素材/kt_module.js，总长:", len(module))

# 检查 kt 函数体中引用的其他未提取标识符（形如 Xxx( 的大写开头函数名）
kt_fn = parts[-1]
calls = set(re.findall(r"[^a-zA-Z0-9_$]([A-Z][A-Za-z0-9_$]{0,3})\(", kt_fn))
print("kt 中调用的大写开头标识符:", sorted(calls))

# ct 定义上下文（699469 位置附近）
print("\n=== ct 定义上下文 ===")
print(js[699380:699600])
