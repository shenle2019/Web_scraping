# -*- coding: utf-8 -*-
"""05 补抓单条回答：分页接口不返回的折叠回答，走单条回答详情接口补漏

背景：members/answers 分页对折叠/隐藏回答不返回（1628-1560=68 条差额）。
单条详情接口 /api/v4/answers/{id} 直接指定 answer id，可绕过折叠过滤。

用法：python 05_补抓单条回答.py <answer_id> [问题标题]

仅限学习研究，禁止商用。
"""
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import unquote

from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(BASE_DIR, r'..\知乎收藏夹x-zse-96签名补环境抓取实战')
STATE_FILE = os.path.join(PREV, r'output\zhihu_state.json')
CHROME = os.path.join(os.environ['LOCALAPPDATA'],
                      r'Google\Chrome\Application\chrome.exe')
STEALTH = r'E:\webspider\Web_scraping\playwright\stealth.min.js'
OUT_DIR = (r'E:\一人公司\公众号写作\Obsidian\testobsidian\知乎高赞'
           r'\丧心病狂刘老湿')

INCLUDE = ('data[*].content,voteup_count,comment_count,created_time,'
           'updated_time,question,author,excerpt,is_normal')

FETCH_ONE = """
(id) => {
  const inc = encodeURIComponent(INCLUDE_STR);
  const url = `/api/v4/answers/${id}?include=${inc}`;
  return fetch(url, {headers: {'x-requested-with': 'fetch'}})
    .then(r => r.json().then(d => ({status: r.status, data: d})))
    .catch(e => ({status: -1, error: String(e)}));
}
"""

ILLEGAL = re.compile(r'[\\/:*?"<>|\r\n\t]')


def clean_name(s, maxlen=50):
    s = ILLEGAL.sub('_', s or '').strip().strip('.')
    return (s[:maxlen] if len(s) > maxlen else s) or '未命名'


def preprocess_html(html):
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


def main():
    answer_id = sys.argv[1]
    fallback_title = sys.argv[2] if len(sys.argv) > 2 else ''

    res = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=CHROME)
        ctx = browser.new_context(storage_state=STATE_FILE)
        ctx.add_init_script(path=STEALTH)
        page = ctx.new_page()
        page.goto('https://www.zhihu.com/people/bingo-liu-66/answers',
                  wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(4000)
        page.evaluate('window.__INCLUDE_STR = %s' % json.dumps(INCLUDE))
        res = page.evaluate(FETCH_ONE.replace('INCLUDE_STR', '__INCLUDE_STR'),
                            answer_id)
        browser.close()

    if res.get('status') != 200:
        print('接口异常: status=%s error=%s' % (res.get('status'),
                                                res.get('error', '')))
        raise SystemExit(1)

    it = res['data']
    q = it.get('question') or {}
    title = q.get('title') or fallback_title or '无标题'
    vote = it.get('voteup_count', 0)
    comment = it.get('comment_count', 0)
    created = (datetime.fromtimestamp(it.get('created_time'))
               .strftime('%Y-%m-%d') if it.get('created_time') else '未知')
    qid = q.get('id') or ''
    url = 'https://www.zhihu.com/question/%s/answer/%s' % (qid, answer_id)
    body_html = it.get('content', '')

    print('[1] 单条回答获取成功:')
    print('    标题: %s' % title)
    print('    赞同: %s  评论: %s  时间: %s' % (vote, comment, created))
    print('    正文长度: %d' % len(body_html or ''))

    if not body_html:
        print('    正文为空（该回答可能已被删除或锁定），中止')
        raise SystemExit(1)

    body_md = md_convert(preprocess_html(body_html), heading_style='ATX',
                         bullets='-').strip()
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
    fname = '%s.md' % clean_name(title)
    out = os.path.join(OUT_DIR, fname)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(content)
    print('[2] 已写入: %s' % out)


if __name__ == '__main__':
    main()
