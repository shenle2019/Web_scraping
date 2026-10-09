# -*- coding: utf-8 -*-
"""大作业：ks.wangxiao.cn（万题库）【每日一练】题目爬取 → 存入 MySQL

需求：
    首页中每个一级标题下随机选择一个二级标题，
    爬取该二级标题对应【每日一练】板块下所有科目、所有日期的
    题目、选项、正确答案（含解析），存储到 MySQL 数据库。

        │ 一级标题：工程类、财会类、金融类 ... （共 12 个）
        │ 二级标题：一级建造师、初级质量工程师 ... （每类随机取 1 个）
        │ 每日一练：listEveryday 页面 → 科目表 + 每天一组题的链接
        │ 题  目：POST /practice/listQuestions（需登录 Cookie）→ JSON

运行方式：
    cd newcases\万题库爬虫
    python 07_ks_wangxiao_spider.py                    # 完整爬取
    python 07_ks_wangxiao_spider.py --dry-run          # 只爬不入库（测试用）
    python 07_ks_wangxiao_spider.py --subjects 1 --days 2   # 每场考试限 1 个科目、2 天（快速测试）

随机策略：
    每个一级标题下随机选一个二级标题；若该考试恰好没有发布过
    每日一练（日期列表为空），会自动换一个随机重试（最多 --max-tries 次），
    可用 --no-reroll 关闭该行为。

依赖（均位于上级 newcases 目录，脚本已自动加入模块搜索路径）：
    - proxy_pool.py（巨量IP 高匿动态代理池，所有请求都走代理）
    - ks_config_local.py（Cookie + MySQL 配置，复制 ks_config_example.py 生成）
"""
import argparse
import hashlib
import html as html_lib
import json
import os
import random
import re
import sys
import time

import pymysql
import requests
from lxml import etree

# 脚本位于子目录：把上级目录（newcases）加入模块搜索路径，
# 以便 import 公共模块 proxy_pool 与本地配置 ks_config_local
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proxy_pool import get_proxies

try:
    from ks_config_local import COOKIE, MYSQL
except ImportError:
    sys.exit(
        "未找到本地配置 ks_config_local.py\n"
        "请复制 ks_config_example.py 为 ks_config_local.py，"
        "填入登录 Cookie 和 MySQL 连接信息"
    )

BASE = "https://ks.wangxiao.cn"
SLEEP_BETWEEN_REQUESTS = 1.5     # 每次请求间隔（秒）
RETRY = 6                        # 单次请求最大重试次数（每次换代理）

# 课程兼容的请求头
BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": COOKIE,
}


class LoginExpired(Exception):
    """Cookie 失效信号：接口返回了登录页"""


# ==================== 一、HTTP 请求（全部走代理池） ====================

def http_get(url, referer=None, retry=RETRY):
    """GET 请求，带重试（每次重试换一个代理）"""
    headers = dict(BASE_HEADERS)
    if referer:
        headers["Referer"] = referer
    for i in range(retry):
        try:
            resp = requests.get(url, headers=headers,
                                proxies=get_proxies(), timeout=20)
            if resp.status_code == 200 and len(resp.text) > 500:
                return resp
            print("    [重试 %d] GET %s -> HTTP %s" % (i + 1, url, resp.status_code))
        except requests.RequestException as exc:
            print("    [重试 %d] GET 异常：%s" % (i + 1, exc))
        time.sleep(1)
    return None


def http_post_json(url, body, referer=None, retry=RETRY):
    """POST JSON 请求，返回解析后的 JSON dict

    若响应是登录页 HTML → 抛出 LoginExpired（提醒更换 Cookie）
    """
    headers = dict(BASE_HEADERS)
    headers["Content-Type"] = "application/json; charset=UTF-8"
    if referer:
        headers["Referer"] = referer
    for i in range(retry):
        try:
            resp = requests.post(url, headers=headers, json=body,
                                 proxies=get_proxies(), timeout=20)
        except requests.RequestException as exc:
            print("    [重试 %d] POST 异常：%s" % (i + 1, exc))
            time.sleep(1)
            continue
        text = resp.text.lstrip()
        if text.startswith("<!DOCTYPE") or text.startswith("<html"):
            # 返回 HTML：说明被重定向到了登录页
            raise LoginExpired("接口返回登录页，Cookie 可能已失效")
        try:
            return resp.json()
        except ValueError:
            print("    [重试 %d] 响应非 JSON（前 80 字符）：%s"
                  % (i + 1, resp.text[:80].replace("\n", " ")))
        time.sleep(1)
    return None


# ==================== 二、页面解析 ====================

def parse_homepage(html):
    """解析首页：返回 [(一级标题, [(二级标题, 每日一练URL), ...]), ...]"""
    tree = etree.HTML(html)
    result = []
    for li in tree.xpath('//ul[@class="first-title"]/li'):
        category = "".join(li.xpath('./p//text()')).strip()
        exams = []
        for a in li.xpath('./div[@class="send-title"]/a'):
            exam_name = "".join(a.xpath('.//text()')).strip()
            href = a.xpath('./@href')[0]
            # 首页链接指向【模拟考试】/TestPaper/list?sign=xxx
            # 换成【每日一练】/practice/listEveryday?sign=xxx，sign 参数不变
            sign = href.split("?")[-1]
            everyday_url = "%s/practice/listEveryday?%s" % (BASE, sign)
            exams.append((exam_name, everyday_url))
        if exams:
            result.append((category, exams))
    return result


def parse_everyday_page(html):
    """解析【每日一练】页面

    返回 (subjects, days)：
      subjects: [(科目名, subsign 或 None), ...]   None 表示页面默认选中的科目
      days:     [{"date": "20261009", "sign": ..., "subsign": ..., "day": ...}, ...]
    """
    tree = etree.HTML(html)
    subjects = []
    for a in tree.xpath('//div[contains(@class,"filter-item")]'
                        '/a[contains(@class,"filter-name")]'):
        name = "".join(a.xpath('.//text()')).strip()
        href = a.xpath('./@href')
        href = href[0] if href else ""
        m = re.search(r"subsign=([0-9a-zA-Z]+)", href)
        subjects.append((name, m.group(1) if m else None))

    days = []
    for ul in tree.xpath('//div[@class="test-panel"]'
                         '//ul[@class="test-item"]'):
        lis = ul.xpath('./li')
        if len(lis) < 4:
            continue
        date = "".join(lis[0].xpath('.//text()')).strip()
        href = lis[3].xpath('./a/@href')
        href = href[0] if href else ""
        # /practice/getQuestion?practiceType=1&sign=jz1&subsign=xxx&day=20261009
        m = re.search(r"sign=([^&]+)&subsign=([^&]+)&day=(\d{8})", href)
        if m:
            days.append({"date": date, "sign": m.group(1),
                         "subsign": m.group(2), "day": m.group(3)})
    return subjects, days


def clean_html(raw):
    """把题目/选项/解析的 HTML 片段转成可读纯文本

    <img> 保留为 [图片:地址]，<br>/<p> 转成换行，其余标签去除
    """
    if not raw:
        return ""
    text = html_lib.unescape(str(raw))
    text = re.sub(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>',
                  r" [图片:\1] ", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html_lib.unescape(text)
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_questions(data_json, meta):
    """把 listQuestions 接口返回的 JSON 解析成题目行列表

    JSON 结构：
        Data: [ { "questions": [题目...], "materials": null, "paperRule": {"title": 题型} },
                { "questions": null, "materials": [ {material, questions} ] }, ... ]
    每个题目：content 题干 / options 选项列表(含 isRight) / textAnalysis 解析
    """
    rows = []
    for seg in data_json.get("Data") or []:
        q_type = ((seg.get("paperRule") or {}).get("title")
                  or seg.get("questionType") or "")
        # 普通题型：题目直接挂在 questions 下
        for q in seg.get("questions") or []:
            rows.append(build_question_row(q, q_type, "", meta))
        # 材料题：1 个背景材料 + n 个题目
        for materi in seg.get("materials") or []:
            material_text = clean_html((materi.get("material") or {}).get("content"))
            for q in materi.get("questions") or []:
                rows.append(build_question_row(q, q_type, material_text, meta))
    return rows


def build_question_row(question, q_type, material_text, meta):
    """把单个题目 dict 转成入库行（dict）"""
    content = clean_html(question.get("content"))
    options = []
    answer_names = []
    for opt in question.get("options") or []:
        name = str(opt.get("name") or "").strip()
        opt_content = clean_html(opt.get("content"))
        is_right = int(opt.get("isRight") or 0)
        options.append({"name": name, "content": opt_content,
                        "isRight": is_right})
        if is_right:
            answer_names.append(name)
    options_text = "\n".join("%s. %s" % (o["name"], o["content"]) for o in options)
    analysis = clean_html(question.get("textAnalysis"))

    q_hash = hashlib.md5(
        ("%s|%s|%s|%s" % (meta["subsign"], meta["day"], content, options_text))
        .encode("utf-8")).hexdigest()

    try:
        question_no = int(question.get("num") or 0)
    except (TypeError, ValueError):
        question_no = 0

    return {
        "category": meta["category"],
        "exam": meta["exam"],
        "exam_sign": meta["sign"],
        "subject": meta["subject"],
        "subsign": meta["subsign"],
        "day": meta["day"],
        "question_type": str(q_type),
        "question_no": question_no,
        "content": content,
        "options_json": json.dumps(options, ensure_ascii=False),
        "options_text": options_text,
        "answer": "".join(answer_names),
        "analysis": analysis,
        "material": material_text,
        "q_hash": q_hash,
    }


# ==================== 三、MySQL 存储 ====================

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ks_questions (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    category      VARCHAR(60)  NOT NULL COMMENT '一级标题（工程类/财会类...）',
    exam          VARCHAR(120) NOT NULL COMMENT '二级标题（一级建造师...）',
    exam_sign     VARCHAR(40)  NOT NULL COMMENT '考试标识 sign',
    subject       VARCHAR(120)          COMMENT '科目（建设工程经济...）',
    subsign       VARCHAR(64)  NOT NULL COMMENT '科目标识 subsign',
    day           CHAR(8)      NOT NULL COMMENT '日期 YYYYMMDD',
    question_type VARCHAR(60)           COMMENT '题型（单项选择题...）',
    question_no   INT                   COMMENT '题目序号',
    content       TEXT                  COMMENT '题干',
    options_json  TEXT                  COMMENT '选项JSON（含isRight正确答案标记）',
    options_text  TEXT                  COMMENT '选项文本（A.xx B.xx）',
    answer        VARCHAR(40)           COMMENT '正确答案（B / ABD）',
    analysis      TEXT                  COMMENT '答案解析',
    material      TEXT                  COMMENT '材料题背景材料',
    q_hash        CHAR(32)     NOT NULL COMMENT '题目指纹（去重用）',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_q_hash (q_hash),
    KEY idx_exam (exam_sign, subsign, day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='万题库每日一练题目'
"""


def connect_mysql():
    """连接 MySQL 并确保库、表存在（库不存在时自动创建）"""
    conf = dict(MYSQL)
    conf.pop("db", None)
    server_conn = pymysql.Connect(autocommit=True, **conf)
    with server_conn.cursor() as cur:
        cur.execute(
            "CREATE DATABASE IF NOT EXISTS `%s` "
            "DEFAULT CHARACTER SET utf8mb4" % MYSQL["db"])
    server_conn.close()

    conn = pymysql.Connect(autocommit=False, **MYSQL)
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    return conn


def save_rows(conn, rows):
    """批量入库（INSERT IGNORE 依靠 q_hash 唯一索引自动去重）"""
    if not rows:
        return 0
    sql = ("INSERT IGNORE INTO ks_questions (category, exam, exam_sign, "
           "subject, subsign, day, question_type, question_no, content, "
           "options_json, options_text, answer, analysis, material, q_hash) "
           "VALUES (%(category)s, %(exam)s, %(exam_sign)s, %(subject)s, "
           "%(subsign)s, %(day)s, %(question_type)s, %(question_no)s, "
           "%(content)s, %(options_json)s, %(options_text)s, %(answer)s, "
           "%(analysis)s, %(material)s, %(q_hash)s)")
    with conn.cursor() as cur:
        inserted = cur.executemany(sql, rows)
    conn.commit()
    return inserted


# ==================== 四、主流程 ====================

LIST_QUESTIONS_API = BASE + "/practice/listQuestions"


def crawl_one_exam(conn, category, exam_name, everyday_url, args, stats):
    """爬取一个二级标题（考试）的【每日一练】全部题目

    返回 True 表示该考试存在每日一练数据（已尝试爬取）；
    返回 False 表示该考试没有发布过每日一练（可换一个重试）。
    """
    sign = everyday_url.split("?")[-1].split("=")[-1]
    print("\n>>> [%s] %s（sign=%s）" % (category, exam_name, sign))

    # 步骤 1：请求【每日一练】页面 → 科目表 + 默认科目每天的链接
    resp = http_get(everyday_url, referer=BASE + "/")
    if resp is None:
        print("    每日一练页面请求失败，跳过")
        stats["exam_failed"] += 1
        return False
    subjects, default_days = parse_everyday_page(resp.text)

    # 步骤 2：整理所有科目 × 所有日期
    #   默认科目（subsign=None）用已抓到的页面数据；
    #   其余科目单独请求 listEveryday?sign=xx&subsign=yy
    day_map = {}           # subsign -> {day: row}
    subject_names = {}     # subsign -> 科目名

    for d in default_days:
        subject_names.setdefault(d["subsign"], "")
        day_map.setdefault(d["subsign"], {})[d["day"]] = d
    # 默认科目名：取 subjects 里 subsign 为 None 的那个
    default_name = next((n for n, s in subjects if s is None), "")
    for subsign in day_map:
        subject_names[subsign] = default_name

    for name, subsign in subjects:
        if subsign is None or subsign in day_map:
            continue
        sub_url = "%s&subsign=%s" % (everyday_url, subsign)
        sub_resp = http_get(sub_url, referer=everyday_url)
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        if sub_resp is None:
            print("    科目[%s]页面请求失败，跳过" % name)
            continue
        _, days = parse_everyday_page(sub_resp.text)
        if days:
            subject_names[subsign] = name
            day_map[subsign] = {d["day"]: d for d in days}

    if not day_map:
        print("    该考试暂无每日一练数据")
        return False

    # 限制科目数 / 天数（测试用；默认不限 = 爬取全部）
    subsign_list = list(day_map.keys())
    if args.subjects > 0:
        subsign_list = subsign_list[:args.subjects]
    if args.days > 0:
        for s in subsign_list:
            kept = sorted(day_map[s].keys(), reverse=True)[:args.days]
            day_map[s] = {k: day_map[s][k] for k in kept}

    print("    科目数：%d，总日期组数：%d"
          % (len(subsign_list), sum(len(day_map[s]) for s in subsign_list)))

    # 步骤 3：逐 (科目, 日期) 请求题目接口
    for subsign in subsign_list:
        subject = subject_names.get(subsign, "")
        for day in sorted(day_map[subsign], reverse=True):
            row = day_map[subsign][day]
            meta = {
                "category": category, "exam": exam_name, "sign": sign,
                "subject": subject, "subsign": subsign, "day": day,
            }
            body = {"practiceType": "1", "sign": sign,
                    "subsign": subsign, "day": day}
            try:
                data = http_post_json(LIST_QUESTIONS_API, body,
                                      referer=everyday_url)
            except LoginExpired as exc:
                sys.exit("\n[中止] %s\n请在浏览器重新登录 ks.wangxiao.cn，"
                         "更新 ks_config_local.py 中的 COOKIE 后重跑。" % exc)
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            if data is None:
                print("    [%s %s] 请求失败，跳过" % (subject, day))
                stats["day_failed"] += 1
                continue

            rows = parse_questions(data, meta)
            if args.dry_run:
                inserted = len(rows)
            else:
                inserted = save_rows(conn, rows)
            stats["total"] += len(rows)
            stats["saved"] += inserted
            print("    [%s %s] 题目 %d 条，入库 %d 条"
                  % (subject, day, len(rows), inserted))
    return True


def main():
    parser = argparse.ArgumentParser(description="万题库每日一练爬虫")
    parser.add_argument("--dry-run", action="store_true",
                        help="只爬取不入库（验证流程用）")
    parser.add_argument("--subjects", type=int, default=0,
                        help="每场考试最多爬几个科目（0=全部）")
    parser.add_argument("--days", type=int, default=0,
                        help="每个科目最多爬几天（0=全部）")
    parser.add_argument("--categories", default="",
                        help="只爬指定一级标题，逗号分隔，如：工程类,财会类")
    parser.add_argument("--no-reroll", action="store_true",
                        help="随机选中的考试若无每日一练数据，不换其他的重试")
    parser.add_argument("--max-tries", type=int, default=6,
                        help="每个一级标题最多尝试几个随机二级标题（默认 6）")
    args = parser.parse_args()

    random.seed()  # 真随机

    # 连接数据库（dry-run 模式跳过）
    conn = None
    if not args.dry_run:
        try:
            conn = connect_mysql()
            print("MySQL 连接成功：%s/%s" % (MYSQL["host"], MYSQL["db"]))
        except pymysql.MySQLError as exc:
            sys.exit("MySQL 连接失败：%s\n请确认 MySQL 已启动，"
                     "并检查 ks_config_local.py 中的 MYSQL 配置。" % exc)

    # 步骤 1：首页 → 一级标题 / 二级标题
    print("=" * 72)
    resp = http_get(BASE + "/")
    if resp is None:
        sys.exit("首页请求失败，请检查代理池配置")
    category_list = parse_homepage(resp.text)
    if args.categories:
        wanted = {c.strip() for c in args.categories.split(",")}
        category_list = [(c, e) for c, e in category_list if c in wanted]
    print("首页解析完成：共 %d 个一级标题" % len(category_list))
    for category, exams in category_list:
        print("  %s：%d 个二级标题" % (category, len(exams)))

    # 步骤 2 + 3：每个一级标题随机选一个二级标题并爬取
    #            选中的考试若没有发布过每日一练，自动随机换一个重试
    stats = {"total": 0, "saved": 0, "exam_failed": 0, "day_failed": 0}
    print("=" * 72)
    for category, exams in category_list:
        order = list(exams)
        random.shuffle(order)  # 随机顺序，每次取第一个
        max_tries = 1 if args.no_reroll else min(args.max_tries, len(order))
        got_data = False
        for idx in range(max_tries):
            exam_name, everyday_url = order[idx]
            if idx > 0:
                print("\n[%s] 上一个考试无每日一练数据，随机换一个重试..." % category)
            got_data = crawl_one_exam(conn, category, exam_name,
                                      everyday_url, args, stats)
            if got_data:
                break
        if not got_data:
            print("[%s] 已尝试 %d 个二级标题，均无每日一练数据"
                  % (category, max_tries))

    # 步骤 4：汇总
    print("\n" + "=" * 72)
    print("爬取完成：共解析题目 %d 条，新入库 %d 条"
          % (stats["total"], stats["saved"]))
    if stats["exam_failed"] or stats["day_failed"]:
        print("（失败：考试页 %d 个，题目批次 %d 个——可重跑，已入库数据不会重复）"
              % (stats["exam_failed"], stats["day_failed"]))
    if conn:
        conn.close()
    print("=" * 72)


if __name__ == "__main__":
    main()
