# -*- coding: utf-8 -*-
"""案例1 建设库：定位企业卡片的重复 DOM 容器结构"""
from lxml import etree

html = open("分析素材/jsk_p3_data.html", encoding="utf-8").read()
doc = etree.HTML(html)

# 1. 找到所有文本精确为"XX有限公司"类的最深元素
hits = []
for el in doc.iter():
    if el.tag in ("a", "h3", "h2", "h4", "span", "div", "p"):
        t = (el.text or "").strip()
        if t.endswith("有限公司") and len(t) < 50:
            hits.append(el)

print("候选元素数:", len(hits))
if hits:
    el = hits[0]
    # 打印该元素及其父容器 2 层
    p1 = el.getparent()
    p2 = p1.getparent() if p1 is not None else None
    print("\n=== 元素本身 ===")
    print(etree.tostring(el, encoding="unicode")[:400])
    print("\n=== 父容器 ===")
    print(etree.tostring(p1, encoding="unicode")[:1200] if p1 is not None else "-")
    print("\n=== 祖父容器（前 1500 字符）===")
    print(etree.tostring(p2, encoding="unicode")[:1500] if p2 is not None else "-")

    # 统计祖父/曾祖父容器下的同类子元素数
    if p2 is not None:
        for depth, anc in enumerate([p1, p2, p2.getparent() if p2 is not None else None]):
            if anc is None:
                continue
            kids = list(anc)
            print("\n祖先层%d <%s class=%r> 直接子元素数: %d" %
                  (depth, anc.tag, anc.get("class"), len(kids)))
            # 检查含有限公司文本的子元素数
            n_com = sum(1 for k in anc.iter() if k.tag in ("a", "h3", "h2")
                        and k.text and "有限公司" in k.text)
            print("   其下含'有限公司'的a/h2/h3数:", n_com)

    # 2. 找到包含全部 20 个企业名的最近公共重复容器
    print("\n=== 20 个企业名的最近重复祖先分析 ===")
    # 找到所有企业名元素
    name_els = []
    for el2 in doc.iter():
        if el2.tag in ("a", "h3", "h2") and el2.text and "有限公司" in el2.text:
            name_els.append(el2)
    print("a/h2/h3 中含'有限公司'元素:", len(name_els))
    if name_els:
        e0 = name_els[0]
        for lvl in range(1, 7):
            anc = e0
            for _ in range(lvl):
                anc = anc.getparent() if anc is not None else None
            if anc is None:
                break
            # 该祖先下有多少个企业名
            n = 0
            for el3 in anc.iter():
                if el3.tag in ("a", "h3", "h2") and el3.text and "有限公司" in el3.text:
                    n += 1
            print("  向上%d层: <%s class=%r> 含企业名数=%d" % (lvl, anc.tag, anc.get("class"), n))
