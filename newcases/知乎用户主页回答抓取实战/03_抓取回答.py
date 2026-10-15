# -*- coding: utf-8 -*-
"""03 正式抓取：知乎用户「丧心病狂刘老湿」全部回答

链路设计：
    Playwright(系统Chrome) + stealth.min.js 消除 webdriver 指纹 + 登录态
    → 页面 JS 上下文内 fetch members/answers 接口（同源自动携带 cookies，
      指纹与真实浏览器一致，服务端风控放行）
    → Python 侧低频翻页（1.2s 间隔），逐页收集到 is_end

输出：
    output/answers_raw_pages.json   逐页原始响应（留档）
    output/answers_all_items.json   合并去重后的全部回答（供解析）

合规：低频单线程，仅限学习研究，禁止商用。
"""
import json
import os
import time

from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(BASE_DIR, r'..\知乎收藏夹x-zse-96签名补环境抓取实战')
STATE_FILE = os.path.join(PREV, r'output\zhihu_state.json')
CHROME = os.path.join(os.environ['LOCALAPPDATA'],
                      r'Google\Chrome\Application\chrome.exe')
STEALTH = r'E:\webspider\Web_scraping\playwright\stealth.min.js'
OUT_DIR = os.path.join(BASE_DIR, 'output')

URL_TOKEN = 'bingo-liu-66'
TARGET = 'https://www.zhihu.com/people/%s/answers' % URL_TOKEN
LIMIT = 20
INTERVAL = 1.2          # 低频间隔（秒）

# 与浏览器捕获一致的新版 include
INCLUDE = ('data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,'
           'annotation_action,annotation_detail,collapse_reason,collapsed_by,'
           'suggest_edit,comment_count,can_comment,content,editable_content,'
           'attachment,voteup_count,reshipment_settings,comment_permission,'
           'created_time,updated_time,review_info,excerpt,paid_info,'
           'reaction_instruction,is_labeled,label_info,'
           'relationship.is_authorized,voting,is_author,is_thanked,is_nothelp,'
           'reaction,vessay_info;'
           'data[*].author.badge[?(type=best_answerer)].topics;'
           'data[*].author.kvip_info;data[*].author.vip_info;'
           'data[*].question.has_publishing_draft,relationship')

FETCH_ONE = """
(offset) => {
  const inc = encodeURIComponent(INCLUDE_STR);
  const url = `/api/v4/members/TOKEN/answers?include=${inc}&offset=${offset}&limit=LIMIT&sort_by=created&ws_qiangzhisafe=0`;
  return fetch(url, {headers: {'x-requested-with': 'fetch'}})
    .then(r => r.json().then(d => ({status: r.status, data: d})))
    .catch(e => ({status: -1, error: String(e)}));
}
""".replace('TOKEN', URL_TOKEN).replace('LIMIT', str(LIMIT))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    pages = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=CHROME)
        ctx = browser.new_context(storage_state=STATE_FILE)
        ctx.add_init_script(path=STEALTH)
        page = ctx.new_page()
        page.goto(TARGET, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(5000)
        # 把 INCLUDE 注入页面 JS 作用域
        page.evaluate('window.__INCLUDE_STR = %s' % json.dumps(INCLUDE))
        fetcher = FETCH_ONE.replace('INCLUDE_STR', '__INCLUDE_STR')

        offset = 0
        totals = None
        page_no = 0
        while True:
            page_no += 1
            res = page.evaluate(fetcher, offset)
            if res.get('status') != 200:
                print('[页 %3d] offset=%d 异常 status=%s error=%s' % (
                    page_no, offset, res.get('status'),
                    str(res.get('error'))[:100]))
                time.sleep(3)
                res = page.evaluate(fetcher, offset)   # 重试一次
                if res.get('status') != 200:
                    print('    重试仍异常，中止。已收集 %d 页' % len(pages))
                    break
            d = res['data']
            pg = d.get('paging', {})
            totals = pg.get('totals', totals)
            items = d.get('data', [])
            pages[offset] = d
            print('[页 %3d] offset=%-4d 本页=%-2d 服务端总数=%s is_end=%s' % (
                page_no, offset, len(items), totals, pg.get('is_end')))
            if pg.get('is_end') or not items:
                break
            offset += LIMIT
            time.sleep(INTERVAL)

        browser.close()

    # 合并去重
    seen, all_items = set(), []
    for off in sorted(pages):
        for item in pages[off].get('data', []):
            if item.get('id') in seen:
                continue
            seen.add(item.get('id'))
            all_items.append(item)

    with open(os.path.join(OUT_DIR, 'answers_raw_pages.json'), 'w',
              encoding='utf-8') as f:
        json.dump({'url_token': URL_TOKEN, 'pages': pages}, f,
                  ensure_ascii=False)
    with open(os.path.join(OUT_DIR, 'answers_all_items.json'), 'w',
              encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False)

    with_content = sum(1 for it in all_items if it.get('content'))
    print('\n抓取完成：%d 页，去重后 %d 条（服务端总数 %s），含全文 %d 条' % (
        len(pages), len(all_items), totals, with_content))
    print('已保存 output/answers_raw_pages.json / answers_all_items.json')


if __name__ == '__main__':
    main()
