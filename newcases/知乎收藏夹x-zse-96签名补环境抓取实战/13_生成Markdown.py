# -*- coding: utf-8 -*-
"""13 生成 Markdown：把抓取到的条目解析为 md 文件，写入 Obsidian 目录

输出目录（用户指定）：E:\\一人公司\\公众号写作\\Obsidian\\testobsidian\\知乎高赞\\10万赞以上的回答\\
    - 每条回答一个 md：序号_标题_作者.md
    - _目录.md：全部条目索引

HTML→Markdown：bs4 预处理（img 懒加载属性、外链解码）+ markdownify 转换。

仅限学习研究，禁止商用。
"""
import json
import os
import re
from datetime import datetime

from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert

SRC = 'output/collection_all_items.json'
OUT_DIR = (r'E:\一人公司\公众号写作\Obsidian\testobsidian\知乎高赞'
           r'\10万赞以上的回答')
INDEX_NAME = '_目录.md'

ILLEGAL = re.compile(r'[\\/:*?"<>|\r\n\t]')


def clean_name(s, maxlen=40):
    """清理 Windows 文件名非法字符并限长"""
    s = ILLEGAL.sub('_', s or '').strip().strip('.')
    if len(s) > maxlen:
        s = s[:maxlen]
    return s or '未命名'


def preprocess_html(html):
    """bs4 预处理知乎正文 HTML：修正图片懒加载、解码外链跳转"""
    soup = BeautifulSoup(html or '', 'html.parser')
    for img in soup.find_all('img'):
        url = (img.get('data-original') or img.get('data-actualsrc')
               or img.get('src') or '')
        if url:
            img['src'] = url
        for attr in ('data-original', 'data-actualsrc', 'data-pid', 'data-rawwidth',
                     'data-rawheight', 'data-caption', 'data-size', 'class'):
            if img.has_attr(attr):
                del img[attr]
    for a in soup.find_all('a'):
        href = a.get('href', '')
        # 知乎外链跳转 https://link.zhihu.com/?target=<encoded>
        m = re.search(r'link\.zhihu\.com/\?target=([^&]+)', href)
        if m:
            from urllib.parse import unquote
            a['href'] = unquote(m.group(1))
        elif href.startswith('/'):
            a['href'] = 'https://www.zhihu.com' + href
        for attr in ('class', 'data-pid', 'rel'):
            if a.has_attr(attr):
                del a[attr]
    for tag in soup.find_all(True):
        for attr in ('data-pid', 'class'):
            if tag.has_attr(attr):
                del tag[attr]
    return str(soup)


def html_to_markdown(html):
    return md_convert(preprocess_html(html), heading_style='ATX',
                      bullets='-').strip()


def main():
    items = json.load(open(SRC, encoding='utf-8'))
    os.makedirs(OUT_DIR, exist_ok=True)
    print('[1] 输出目录:', OUT_DIR)
    print('    待处理条目:', len(items))

    index_lines = ['# 知乎收藏夹「10万赞以上的回答」全量存档', '',
                   '> 来源：https://www.zhihu.com/collection/323709385',
                   '> 共 %d 条（本目录逐条存档，网络图片在 Obsidian 中直接渲染）'
                   % len(items), '', '| # | 标题 | 作者 | 赞同 | 文件 |',
                   '| --- | --- | --- | --- | --- |']

    ok, skipped = 0, []
    for i, it in enumerate(items, 1):
        c = it.get('content', {}) or {}
        ctype = c.get('type', 'answer')
        title = (c.get('question', {}) or {}).get('title') or c.get('title') or '无标题'
        author = (c.get('author', {}) or {}).get('name') or '匿名用户'
        vote = c.get('voteup_count', 0)
        comment = c.get('comment_count', 0)
        url = c.get('url', '')
        body_html = c.get('content', '')
        collected_ts = it.get('created')
        if isinstance(collected_ts, str) and len(collected_ts) >= 10:
            collected = collected_ts[:10]        # ISO 形式：2025-03-13T04:44:53+08:00
        elif isinstance(collected_ts, (int, float)):
            collected = datetime.fromtimestamp(collected_ts).strftime('%Y-%m-%d')
        else:
            collected = '未知'
        created = (datetime.fromtimestamp(c.get('created_time')).strftime('%Y-%m-%d')
                   if c.get('created_time') else '未知')

        if not body_html:
            skipped.append((i, title, '无正文(可能已删除/视频)'))
            body_md = '*（本条无正文内容，可能已被删除或为特殊类型）*'
        else:
            body_md = html_to_markdown(body_html)

        note = [] if ctype == 'answer' else ['', '> 注：本条为「%s」类型' % ctype]
        content = '\n'.join([
            '# %s' % title,
            '',
            '> **作者**：%s　|　**赞同**：%s　|　**评论**：%s' % (author, vote, comment),
            '> **源链接**：%s' % url,
            '> **回答时间**：%s　|　**收藏时间**：%s' % (created, collected),
            *note,
            '',
            '---',
            '',
            body_md,
            '',
        ])

        fname = '%03d_%s_%s.md' % (i, clean_name(title), clean_name(author, 12))
        with open(os.path.join(OUT_DIR, fname), 'w', encoding='utf-8') as f:
            f.write(content)
        index_lines.append('| %d | %s | %s | %s | [%s](./%s) |' % (
            i, title.replace('|', '丨'), author, vote, fname, fname))
        ok += 1
        if i % 50 == 0:
            print('    已生成 %d/%d' % (i, len(items)))

    with open(os.path.join(OUT_DIR, INDEX_NAME), 'w', encoding='utf-8') as f:
        f.write('\n'.join(index_lines) + '\n')

    print('\n[2] 完成：写入 %d 个 md 文件 + 1 个目录索引' % ok)
    if skipped:
        print('    无正文条目 %d 条:' % len(skipped))
        for i, t, why in skipped:
            print('      #%d %s -> %s' % (i, t[:30], why))


if __name__ == '__main__':
    main()
