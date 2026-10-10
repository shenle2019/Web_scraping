# -*- coding: utf-8 -*-
"""案例1 建设库：精细解析 jsk_p3_data.html 的企业列表 DOM 结构"""
from lxml import etree

html = open("分析素材/jsk_p3_data.html", encoding="utf-8").read()
doc = etree.HTML(html)
if doc is None:
    raise SystemExit("HTML 解析失败")

print("=== 尝试多种 XPath 定位企业卡片 ===")
candidates = [
    '//div[contains(@class,"search-list")]//li',
    '//div[contains(@class,"list")]//li',
    '//ul[contains(@class,"list")]//li',
    '//div[contains(@class,"result")]//li',
    '//li[contains(@class,"item")]',
    '//div[contains(@class,"company")]',
]
for xp in candidates:
    els = doc.xpath(xp)
    if els:
        print("\nXPATH 命中:", xp, "->", len(els), "个元素")
        el = els[1] if len(els) > 1 else els[0]
        seg = etree.tostring(el, encoding="unicode")[:900]
        print(seg)
        break
else:
    print("候选 XPath 均未命中，转储包含'有限公司'的第一个祖先容器:")
    # 找到第一个含企业名的元素并向上取 3 层
    names = doc.xpath('//*[contains(text(),"有限公司")]')
    print("含'有限公司'文本元素数:", len(names))
    if names:
        el = names[0]
        for _ in range(3):
            el = el.getparent()
            if el is None:
                break
        if el is not None:
            print(etree.tostring(el, encoding="unicode")[:1500])

print("\n=== 分页区域 ===")
pager = doc.xpath('//*[contains(@class,"page") or contains(@class,"pag")]')
print("分页相关元素:", len(pager))
for p in pager[:6]:
    txt = " ".join(t.strip() for t in p.itertext() if t.strip())[:150]
    print("  <%s class=%r> %s" % (p.tag, p.get("class"), txt))

print("\n=== 每页企业数统计（h3/a/span 内企业名）===")
uniq = []
for k in ("a", "h3", "h2", "span", "div"):
    for el in doc.iter(k):
        t = (el.text or "").strip()
        if t.endswith("有限公司") or t.endswith("股份有限公司"):
            if t not in uniq:
                uniq.append(t)
print("去重企业名:", len(uniq))
for n in uniq[:12]:
    print("  -", n)
