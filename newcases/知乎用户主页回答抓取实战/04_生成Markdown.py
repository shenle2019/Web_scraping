# -*- coding: utf-8 -*-
"""04 生成 Markdown：把抓取到的回答解析为 md 文件，写入用户指定 Obsidian 目录

输出目录（用户指定）：E:\\一人公司\\公众号写作\\Obsidian\\testobsidian\\知乎高赞\\丧心病狂刘老湿\\
    - 每条回答一个 md：序号_问题标题.md（作者均为刘老湿本人）
    - _目录.md：全部条目索引

HTML→Markdown：bs4 预处理（图片懒加载、外链解码）+ markdownify 转换。

仅限学习研究，禁止商用。
"""
import json
import os
import re
from datetime import datetime
from urllib.parse import unquote

from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'output', 'answers_all_items.json')
OUT_DIR = (r'E:\一人公司\公众号写作\Obsidian\testobsidian\知乎高赞'
           r'\丧心病狂刘老湿')
INDEX_NAME = '_目录.md'

ILLEGAL = re.compile(r'[\\/:*?"<>|\r\n\t]')


def clean_name(s, maxlen=50):
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
        for attr in ('data-original', 'data-actualsrc', 'data-pid',
                     'data-rawwidth', 'data-rawheight', 'data-caption',
                     'data-size', 'class'):
            if img.has_attr(attr):
                del img[attr]
    for a in soup.find_all('a'):
        href = a.get('href', '')
        # 知乎外链跳转 https://link.zhihu.com/?target=<encoded>
        m = re.search(r'link\.zhihu\.com/\?target=([^&]+)', href)
        if m:
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

    index_lines = ['# 知乎用户「丧心病狂刘老湿」回答全量存档', '',
                   '> 来源：https://www.zhihu.com/people/bingo-liu-66/answers',
                   '> 共 %d 条（本目录逐条存档，网络图片在 Obsidian 中直接渲染）'
                   % len(items), '',
                   '| # | 标题 | 赞同 | 评论 | 回答时间 | 文件 |',
                   '| --- | --- | --- | --- | --- | --- |']

    ok, skipped = 0, []
    for i, it in enumerate(items, 1):
        q = it.get('question') or {}
        title = q.get('title') or '无标题'
        vote = it.get('voteup_count', 0)
        comment = it.get('comment_count', 0)
        created = (datetime.fromtimestamp(it.get('created_time'))
                   .strftime('%Y-%m-%d') if it.get('created_time') else '未知')
        qid = q.get('id') or ''
        aid = it.get('id') or ''
        url = ('https://www.zhihu.com/question/%s/answer/%s' % (qid, aid)
               if qid and aid else it.get('url', ''))
        body_html = it.get('content', '')

        if not body_html:
            skipped.append((i, title, '无正文(可能已删除/折叠)'))
            body_md = '*（本条无正文内容，可能已被删除或折叠）*'
        else:
            body_md = html_to_markdown(body_html)

        content = '\n'.join([
            '# %s' % title,
            '',
            '> **作者**：丧心病狂刘老湿　|　**赞同**：%s　|　**评论**：%s' % (
                vote, comment),
            '> **源链接**：%s' % url,
            '> **回答时间**：%s' % created,
            '',
            '---',
            '',
            body_md,
            '',
        ])

        fname = '%04d_%s.md' % (i, clean_name(title))
        with open(os.path.join(OUT_DIR, fname), 'w', encoding='utf-8') as f:
            f.write(content)
        index_lines.append('| %d | %s | %s | %s | %s | [%s](./%s) |' % (
            i, title.replace('|', '丨'), vote, comment, created, fname, fname))
        ok += 1
        if i % 100 == 0:
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
