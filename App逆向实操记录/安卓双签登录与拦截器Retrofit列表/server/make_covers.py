# -*- coding: utf-8 -*-
"""生成本地海报占位图（纯标准库，不依赖 Pillow）。

每张图是一个 300x420 的竖向渐变，颜色按 id 从调色板里取。
运行：python make_covers.py
"""
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "covers")

PALETTE = [
    ((28, 40, 78), (96, 140, 200)),
    ((78, 18, 26), (200, 96, 72)),
    ((16, 58, 48), (110, 190, 150)),
    ((44, 30, 60), (150, 110, 190)),
    ((70, 44, 12), (210, 160, 80)),
    ((18, 34, 56), (90, 130, 170)),
    ((62, 20, 40), (190, 100, 130)),
    ((30, 30, 30), (140, 140, 140)),
    ((20, 46, 60), (100, 170, 190)),
    ((36, 24, 60), (130, 100, 200)),
]

W, H = 300, 420


def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(path, top, bottom):
    raw = bytearray()
    for y in range(H):
        t = y / (H - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        raw.append(0)                      # filter type: none
        raw.extend(bytes((r, g, b)) * W)   # 每行重复同一个颜色
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def ensure_covers(count=10):
    os.makedirs(OUT_DIR, exist_ok=True)
    for i in range(1, count + 1):
        path = os.path.join(OUT_DIR, "%d.png" % i)
        if not os.path.exists(path):
            top, bottom = PALETTE[(i - 1) % len(PALETTE)]
            write_png(path, top, bottom)
    return OUT_DIR


if __name__ == "__main__":
    out = ensure_covers()
    print("covers ->", out)
