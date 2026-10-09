# -*- coding: utf-8 -*-
"""把 MySQL 里爬到的题目导出成 Excel，直接用 Excel 就能查看结果

用法：
    cd newcases\万题库爬虫
    python 10_export_questions.py                  # 导出全部 → newcases\ks_questions.xlsx
    python 10_export_questions.py --limit 200      # 只导出前 200 条（快速预览）
    python 10_export_questions.py --category 财会类  # 只导出某一个一级标题
"""
import argparse
import os
import re
import sys
import warnings

import pandas as pd
import pymysql

# 脚本位于子目录：把上级目录（newcases）加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ks_config_local import MYSQL

warnings.filterwarnings("ignore")  # 忽略 pandas 对 pymysql 连接的提示

# Excel 不允许的控制字符（如 \x07 空格符）先清洗掉
ILLEGAL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean_value(value):
    if not isinstance(value, str):
        return value
    value = ILLEGAL_CHARS.sub("", value)
    return value[:32000]  # 单元格上限 32767 字符，超长截断

# 数据库字段 -> Excel 列名
COLUMNS = {
    "category": "一级标题", "exam": "二级标题", "subject": "科目",
    "day": "日期", "question_type": "题型", "question_no": "序号",
    "content": "题干", "options_text": "选项", "answer": "正确答案",
    "analysis": "解析", "material": "材料",
}


def main():
    parser = argparse.ArgumentParser(description="导出万题库题目到 Excel")
    parser.add_argument("--limit", type=int, default=0,
                        help="最多导出多少条（0=全部）")
    parser.add_argument("--category", default="",
                        help="只导出指定一级标题，如：财会类")
    default_out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "ks_questions.xlsx")
    parser.add_argument("--out", default=default_out,
                        help="输出文件名（默认输出到 newcases 目录）")
    args = parser.parse_args()

    where, params = "", []
    if args.category:
        where = "WHERE category = %s"
        params.append(args.category)
    limit = "LIMIT %d" % args.limit if args.limit > 0 else ""

    sql = ("SELECT category, exam, subject, day, question_type, question_no, "
           "content, options_text, answer, analysis, material "
           "FROM ks_questions %s "
           "ORDER BY category, exam, subject, day DESC, question_no %s"
           % (where, limit))

    conn = pymysql.Connect(autocommit=True, **MYSQL)
    df = pd.read_sql(sql, conn, params=params).rename(columns=COLUMNS)
    stat = pd.read_sql(
        "SELECT category AS 一级标题, exam AS 二级标题, COUNT(*) AS 题目数 "
        "FROM ks_questions GROUP BY category, exam "
        "ORDER BY category, exam", conn)
    conn.close()

    # 清洗控制字符，防止 openpyxl 报 IllegalCharacterError
    for col in df.columns:
        df[col] = df[col].map(clean_value)

    with pd.ExcelWriter(args.out, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="题目明细", index=False)
        stat.to_excel(writer, sheet_name="统计", index=False)

    print("导出完成：%s（共 %d 条题目）" % (args.out, len(df)))
    print()
    print(stat.to_string(index=False))
    print()

    # 控制台预览第 1 条，确认内容无误
    if len(df) > 0:
        r = df.iloc[0]
        print("=" * 60)
        print("样例第 1 条（Excel 里每一行都是这样的数据）：")
        for col in df.columns:
            value = str(r[col])
            if len(value) > 150:
                value = value[:150] + " ..."
            print("%s：%s" % (col, value))


if __name__ == "__main__":
    main()
