# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

libshield.so 静态取证：
  1) 读 ELF 头确认架构
  2) 解析 .dynsym，列出导出的函数符号（找 Java_* / JNI_*）
  3) 扫字符串，确认动态注册的目标类名与 okhttp 依赖
不执行 so，不联网。

用法：python 01_inspect_so.py [so路径] [--out 结果日志]
"""
import argparse
import io
import os
import struct
import sys


def parse_elf(data):
    if data[:4] != b"\x7fELF":
        raise SystemExit("不是 ELF 文件")
    ei_class = data[4]
    is64 = ei_class == 2
    machine = struct.unpack_from("<H", data, 18)[0]
    arch = {0x28: "ARM(32)", 0xB7: "AArch64", 0x3E: "x86-64"}.get(machine, hex(machine))
    if is64:
        e_shoff, = struct.unpack_from("<Q", data, 0x28)
        e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", data, 0x3A)
    else:
        e_shoff, = struct.unpack_from("<I", data, 0x20)
        e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", data, 0x2E)

    sections = []
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        if is64:
            name, typ, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from("<IIQQQQIIQQ", data, off)
        else:
            name, typ, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from("<IIIIIIIIII", data, off)
        sections.append({"name_off": name, "type": typ, "offset": offset, "size": size,
                         "link": link, "entsize": entsize})
    shstr = sections[e_shstrndx]
    shstr_data = data[shstr["offset"]:shstr["offset"] + shstr["size"]]

    def sec_name(o):
        end = shstr_data.find(b"\x00", o)
        return shstr_data[o:end].decode("utf-8", "replace")

    for s in sections:
        s["name"] = sec_name(s["name_off"])
    return is64, arch, sections


def dyn_symbols(data, sections, is64):
    dynsym = next((s for s in sections if s["name"] == ".dynsym"), None)
    dynstr = next((s for s in sections if s["name"] == ".dynstr"), None)
    if not dynsym or not dynstr:
        return []
    strtab = data[dynstr["offset"]:dynstr["offset"] + dynstr["size"]]
    out = []
    ent = dynsym["entsize"] or (24 if is64 else 16)
    count = dynsym["size"] // ent
    for i in range(count):
        off = dynsym["offset"] + i * ent
        if is64:
            name_off, info, other, shndx, value, size = struct.unpack_from("<IBBHQQ", data, off)
        else:
            name_off, value, size, info, other, shndx = struct.unpack_from("<IIIBBH", data, off)
        end = strtab.find(b"\x00", name_off)
        name = strtab[name_off:end].decode("utf-8", "replace")
        typ = info & 0xF
        if name and typ == 2:  # STT_FUNC
            out.append((name, value, size))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("so", nargs="?", default=r"apks\xhs\libshield.so")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    logs = []

    def log(line):
        line = line if isinstance(line, str) else str(line)
        print(line)
        logs.append(line)

    data = open(args.so, "rb").read()
    is64, arch, sections = parse_elf(data)
    log("文件 = %s（%d 字节）" % (os.path.abspath(args.so), len(data)))
    log("架构 = %s，ELF%s" % (arch, "64" if is64 else "32"))

    funcs = dyn_symbols(data, sections, is64)
    java_funcs = [f for f in funcs if f[0].startswith("Java_")]
    log("导出函数总数 = %d，其中 Java_* 静态注册符号 = %d" % (len(funcs), len(java_funcs)))
    for name, value, size in java_funcs[:10]:
        log("  %s @0x%x size=%d" % (name, value, size))
    for key in ("JNI_OnLoad", "JNI_OnUnload"):
        hit = [f for f in funcs if f[0] == key]
        log("  %s：%s" % (key, "有" if hit else "无"))

    for needle in (b"com/xingin/shield/http/XhsHttpInterceptor", b"initializeNative",
                   b"okhttp3/Interceptor", b"xy-platform-info", b"shield"):
        log("字符串 %-46s 出现 %d 次" % (needle.decode(), data.count(needle)))
    log("结论：so 用动态注册把 native 方法挂到 XhsHttpInterceptor 上，intercept 依赖 okhttp3 类型，"
        "纯 unidbg 调用必须先补齐这些 Java 环境。")
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(logs) + "\n")
        print("已写入 %s" % os.path.abspath(args.out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
