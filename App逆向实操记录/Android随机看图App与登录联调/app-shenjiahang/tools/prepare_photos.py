# -*- coding: utf-8 -*-
"""把写真素材压缩成 App 内置图片（仅限学习研究，禁止商用）。

用法（在 app-shenjiahang 工程目录下执行，tools/ 与 app/ 平级）：
  python tools/prepare_photos.py --src "D:\\photos"   # 指定素材目录
  python tools/prepare_photos.py --placeholders       # 生成占位图（无私人照片时用于编译演示）

处理：EXIF 方向校正 -> 居中裁成 3:4 -> 缩放到 1080x1440 -> JPEG q86。
输出：app/src/main/res/drawable-nodpi/photo_01.jpg ...
      tools/out/photos_manifest.json（原始文件名、字节数、md5，便于核对）
"""
import argparse
import glob
import hashlib
import json
import os
from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
OUT_DIR = os.path.join(PROJECT, "app", "src", "main", "res", "drawable-nodpi")
MANIFEST = os.path.join(HERE, "out", "photos_manifest.json")
DEFAULT_SRC = ""
TARGET_SIZE = (1080, 1440)
COUNT = 11


def crop_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    if w / h > target_ratio:          # 太宽，裁左右
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:                              # 太高，裁上下
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img.resize(TARGET_SIZE, Image.LANCZOS)


def make_placeholder(index):
    top, bottom = (255, 246, 243), (243, 205, 210)
    img = Image.new("RGB", TARGET_SIZE)
    d = ImageDraw.Draw(img)
    for y in range(TARGET_SIZE[1]):
        t = y / (TARGET_SIZE[1] - 1)
        d.line([(0, y), (TARGET_SIZE[0], y)],
               fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    # 简单爱心图形占位
    import math
    cx, cy, size = TARGET_SIZE[0] // 2, TARGET_SIZE[1] // 2 - 60, 210
    pts = []
    for i in range(160):
        t = 2 * math.pi * i / 160
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * size / 32, cy - y * size / 32))
    d.polygon(pts, fill=(236, 158, 164))
    d.text((cx - 30, cy + 180), "%02d" % index, fill=(160, 118, 118))
    return img


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=DEFAULT_SRC, help="素材目录，仅读取 *.jpg / *.JPG")
    parser.add_argument("--placeholders", action="store_true", help="不读素材，生成占位图")
    parser.add_argument("--out", default=OUT_DIR, help="输出目录，默认 app/src/main/res/drawable-nodpi")
    args = parser.parse_args()
    if not args.placeholders and not args.src:
        parser.error("请用 --src 指定素材目录，或加 --placeholders 生成占位图")

    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)

    files = []
    if not args.placeholders:
        files = sorted(glob.glob(os.path.join(args.src, "*.jpg"))
                       + glob.glob(os.path.join(args.src, "*.JPG")))
    records = []
    for i in range(COUNT):
        out_path = os.path.join(out_dir, "photo_%02d.jpg" % (i + 1))
        if files:
            src = files[i % len(files)]
            with Image.open(src) as raw:
                img = ImageOps.exif_transpose(raw).convert("RGB")
                img = crop_3_4(img)
                img.save(out_path, "JPEG", quality=86, optimize=True, progressive=True)
            with open(src, "rb") as f:
                src_md5 = hashlib.md5(f.read()).hexdigest()
            records.append({
                "index": i + 1,
                "source": os.path.basename(src),
                "source_bytes": os.path.getsize(src),
                "source_md5": src_md5,
                "out_bytes": os.path.getsize(out_path),
            })
        else:
            make_placeholder(i + 1).save(out_path, "JPEG", quality=88, optimize=True)
            records.append({"index": i + 1, "source": "placeholder",
                            "out_bytes": os.path.getsize(out_path)})
        print("%-14s %7d bytes" % (os.path.basename(out_path), os.path.getsize(out_path)))

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump({"generated_from": "placeholders" if args.placeholders else args.src,
                   "photos": records}, f, ensure_ascii=False, indent=2)
    total = sum(r["out_bytes"] for r in records)
    print("TOTAL %.2f MB -> %s" % (total / 1024 / 1024, out_dir))


if __name__ == "__main__":
    main()
