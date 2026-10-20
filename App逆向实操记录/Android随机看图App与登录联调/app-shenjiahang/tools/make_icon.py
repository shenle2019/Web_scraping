# -*- coding: utf-8 -*-
"""生成「沈嘉杭呀」App 图标（纯 PIL 绘制，无外部素材，可复现；仅限学习研究，禁止商用）。

运行位置：把 tools/ 放在 app-shenjiahang/ 下（与 app/ 平级），执行后会直接写入
res/mipmap-{mdpi..xxxhdpi}/ic_launcher.png 与 res/drawable-nodpi/ic_launcher_foreground.png。

输出：
  out/icon_1024.png            完整方图（用于 legacy mipmap 缩放）
  out/ic_launcher_foreground.png  自适应图标前景（透明画布 + 圆角贴纸）
  out/icon_bg.txt              自适应图标背景色（从图标四角采样）

设计：奶油粉渐变底 + 倾斜的白色拍立得相框 + 抽象宝宝剪影 + 爱心/星芒。
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps

S = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def vgrad(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))


def radial_highlight(size, color, alpha):
    w, h = size
    mask = Image.radial_gradient("L").resize((w, h))
    mask = ImageOps.invert(mask)
    layer = Image.new("RGBA", (w, h), color + (0,))
    layer.putalpha(mask.point(lambda v: int(v * alpha / 255)))
    return layer


def heart_polygon(cx, cy, size, points=140):
    import math
    pts = []
    for i in range(points):
        t = 2 * math.pi * i / points
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * size / 32.0, cy - y * size / 32.0))
    return pts


def star_polygon(cx, cy, r, inner=0.28):
    pts = []
    for i in range(8):
        import math
        ang = math.pi / 2 * (i / 2.0) + (0 if i % 2 == 0 else math.pi / 4)
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(ang), cy - rr * math.sin(ang)))
    return pts


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


# ---------- 背景 ----------
canvas = vgrad((S, S), (255, 247, 243), (247, 205, 212)).convert("RGBA")
canvas.alpha_composite(radial_highlight((S, S), (255, 255, 255), 130))
bg_layer = canvas.copy()

# ---------- 拍立得（单独图层，整体旋转） ----------
card_w, card_h, card_r = 500, 600, 46
layer = Image.new("RGBA", (card_w + 80, card_h + 80), (0, 0, 0, 0))
ld = ImageDraw.Draw(layer)
ox, oy = 40, 40

# 阴影
shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle([ox, oy + 8, ox + card_w, oy + card_h + 8], radius=card_r,
                     fill=(120, 80, 80, 70))
shadow = shadow.filter(ImageFilter.GaussianBlur(26))
layer.alpha_composite(shadow)

# 卡纸
ld.rounded_rectangle([ox, oy, ox + card_w, oy + card_h], radius=card_r,
                     fill=(255, 253, 251, 255))

# 相片区域（渐变底）
pw = card_w - 60
photo = vgrad((pw, pw), (252, 231, 228), (243, 199, 205)).convert("RGBA")
pm = rounded_mask((pw, pw), 30)
layer.paste(photo, (ox + 30, oy + 30), pm)

# 宝宝插画（简洁、无面部细节）
dr = ImageDraw.Draw(layer)
cx = ox + card_w // 2
base_y = oy + 30 + pw - 8

# 身体（裹布）
dr.rounded_rectangle([cx - 150, base_y - 190, cx + 150, base_y + 40], radius=110,
                     fill=(253, 247, 241, 255))
# 头部
dr.ellipse([cx - 104, base_y - 330, cx + 104, base_y - 122], fill=(255, 228, 210, 255))
# 耳朵
dr.ellipse([cx - 122, base_y - 248, cx - 92, base_y - 206], fill=(255, 224, 205, 255))
dr.ellipse([cx + 92, base_y - 248, cx + 122, base_y - 206], fill=(255, 224, 205, 255))
# 头发小卷
dr.arc([cx - 18, base_y - 356, cx + 40, base_y - 306], 200, 340, fill=(199, 154, 125, 255), width=13)
dr.arc([cx - 46, base_y - 346, cx + 10, base_y - 300], 190, 320, fill=(199, 154, 125, 255), width=11)
# 闭眼
dr.arc([cx - 62, base_y - 250, cx - 22, base_y - 220], 200, 340, fill=(138, 106, 92, 255), width=7)
dr.arc([cx + 22, base_y - 250, cx + 62, base_y - 220], 200, 340, fill=(138, 106, 92, 255), width=7)
# 腮红
dr.ellipse([cx - 76, base_y - 212, cx - 40, base_y - 190], fill=(248, 191, 195, 190))
dr.ellipse([cx + 40, base_y - 212, cx + 76, base_y - 190], fill=(248, 191, 195, 190))
# 小嘴
dr.arc([cx - 12, base_y - 196, cx + 12, base_y - 178], 20, 160, fill=(214, 140, 132, 255), width=5)

# 相纸下沿的小爱心
dr.polygon(heart_polygon(cx, oy + card_h - 62, 46), fill=(233, 143, 151, 255))

rotated = layer.rotate(-6, resample=Image.BICUBIC, expand=True)

# 主体画在透明层上，便于单独导出自适应图标前景
motif = Image.new("RGBA", (S, S), (0, 0, 0, 0))
motif.alpha_composite(rotated, (S // 2 - rotated.width // 2, S // 2 - rotated.height // 2 - 4))

# ---------- 点缀：爱心 + 星芒 ----------
d = ImageDraw.Draw(motif)
d.polygon(heart_polygon(806, 236, 86), fill=(232, 128, 140, 255))
d.polygon(star_polygon(268, 316, 30), fill=(255, 255, 255, 235))
d.polygon(star_polygon(760, 742, 24), fill=(240, 186, 150, 255))
d.polygon(star_polygon(300, 712, 16), fill=(255, 255, 255, 210))

canvas.alpha_composite(motif)

icon = canvas.convert("RGB")
icon.save(os.path.join(OUT, "icon_1024.png"))

# ---------- 自适应图标前景：透明底 + 居中的拍立得主体 ----------
bbox = motif.getbbox()
pad = 18
bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
        min(S, bbox[2] + pad), min(S, bbox[3] + pad))
body = motif.crop(bbox)
side = max(body.size)
scale = 760.0 / side
body = body.resize((max(1, int(body.width * scale)), max(1, int(body.height * scale))),
                   Image.LANCZOS)
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
fg.alpha_composite(body, ((S - body.width) // 2, (S - body.height) // 2))
fg.save(os.path.join(OUT, "ic_launcher_foreground.png"))

# ---------- 背景色采样 ----------
px = icon.load()
r, g, b = px[12, 12]
with open(os.path.join(OUT, "icon_bg.txt"), "w", encoding="utf-8") as f:
    f.write("#%02X%02X%02X" % (r, g, b))

print("icon_1024.png", icon.size)
print("ic_launcher_foreground.png", fg.size)
print("bg", "#%02X%02X%02X" % (r, g, b))

# ---------- 直接输出到 Android 工程 ----------
import shutil
RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "src", "main", "res")
DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
for folder, size in DENSITIES.items():
    target = os.path.join(RES, "mipmap-" + folder)
    os.makedirs(target, exist_ok=True)
    small = icon.resize((size, size), Image.LANCZOS).convert("RGBA")
    small.putalpha(rounded_mask((size, size), max(6, int(size * 0.22))))
    small.save(os.path.join(target, "ic_launcher.png"))

node = os.path.join(RES, "drawable-nodpi")
os.makedirs(node, exist_ok=True)
shutil.copyfile(os.path.join(OUT, "ic_launcher_foreground.png"),
                os.path.join(node, "ic_launcher_foreground.png"))
print("mipmaps written to", RES)
