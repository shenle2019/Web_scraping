# -*- coding: utf-8 -*-
"""把 MySQL 里的题目生成一个单文件 HTML 查看器（双击即开，无需服务器）

功能：
    - 左侧类目导航：一级标题 / 二级标题双击筛选
    - 顶部搜索：题干 / 选项 / 答案 / 解析 关键词（空格分隔多个词）
    - 题型、科目下拉筛选；分页浏览
    - 正确答案绿色高亮，解析与材料可折叠

用法：
    cd newcases\万题库爬虫
    python 11_make_html_viewer.py                    # 生成 newcases\ks_questions.html
    python 11_make_html_viewer.py --out 题目查看.html  # 自定义输出文件名
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime

import pymysql

# 脚本位于子目录：把上级目录（newcases）加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ks_config_local import MYSQL

# Excel/HTML 都不安全的控制字符先清掉
ILLEGAL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

SQL = ("SELECT id, category, exam, subject, day, question_type, "
       "question_no, content, options_json, answer, analysis, material "
       "FROM ks_questions "
       "ORDER BY category, exam, subject, day DESC, question_no")


def clean(text):
    if text is None:
        return ""
    return ILLEGAL_CHARS.sub("", str(text))


TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>万题库《每日一练》题目查看器</title>
<style>
:root{--accent:#2563eb;--ok:#16a34a;--bg:#f3f5f9;--line:#e5e7eb;--txt:#1f2937;--sub:#6b7280;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;background:var(--bg);color:var(--txt);}
header{position:sticky;top:0;z-index:20;background:#fff;border-bottom:1px solid var(--line);padding:10px 18px;box-shadow:0 1px 4px rgba(0,0,0,.06);}
.h-row1{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;}
.h-row1 h1{font-size:17px;color:#111827;}
.stats{font-size:12.5px;color:var(--sub);}
.h-row2{display:flex;gap:10px;margin-top:10px;flex-wrap:wrap;align-items:center;}
.h-row2 input[type=text]{flex:1;min-width:220px;padding:8px 12px;border:1px solid var(--line);border-radius:8px;font-size:14px;outline:none;}
.h-row2 input[type=text]:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(37,99,235,.12);}
.h-row2 select{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:14px;background:#fff;max-width:240px;}
.h-row2 button{padding:8px 14px;border:1px solid var(--line);border-radius:8px;background:#fff;font-size:14px;cursor:pointer;}
.h-row2 button:hover{border-color:var(--accent);color:var(--accent);}
.layout{display:flex;max-width:1280px;margin:0 auto;padding:16px;gap:16px;align-items:flex-start;}
aside{width:250px;flex:none;background:#fff;border:1px solid var(--line);border-radius:10px;padding:8px;position:sticky;top:112px;max-height:calc(100vh - 130px);overflow:auto;}
.sb-item{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:7px 10px;border-radius:7px;font-size:13.5px;cursor:pointer;margin:2px 0;}
.sb-item:hover{background:#f1f5f9;}
.sb-item.active{background:#dbeafe;color:#1d4ed8;font-weight:600;}
.sb-all{font-weight:600;}
.sb-cat{font-weight:600;margin-top:6px;}
.sb-exam{padding-left:22px;color:#475569;font-size:13px;}
.sb-item .cnt{font-size:12px;color:var(--sub);flex:none;}
.sb-item.active .cnt{color:#1d4ed8;}
main{flex:1;min-width:0;}
.list-info{font-size:13px;color:var(--sub);margin:2px 2px 10px;}
.empty{padding:50px;text-align:center;color:#94a3b8;font-size:14px;background:#fff;border-radius:10px;border:1px dashed var(--line);}
.q-card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:13px;}
.q-badges{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:9px;}
.badge{font-size:11.5px;background:#eef2ff;color:#3730a3;padding:2px 9px;border-radius:999px;white-space:nowrap;}
.b-type{background:#dbeafe;color:#1d4ed8;font-weight:700;}
.q-text{font-size:15px;line-height:1.75;white-space:pre-wrap;}
.opts{margin-top:9px;}
.opt{padding:6px 11px;border-radius:7px;margin:5px 0;background:#f8fafc;line-height:1.65;white-space:pre-wrap;font-size:14px;}
.opt.right{background:#ecfdf5;color:#065f46;font-weight:600;border:1px solid #a7f3d0;}
.tick{color:var(--ok);font-weight:bold;}
.ans-row{margin-top:10px;font-size:14px;}
.ans{background:var(--ok);color:#fff;padding:2px 12px;border-radius:6px;font-weight:700;letter-spacing:1px;}
.ans-none{color:#94a3b8;font-weight:400;}
details.fold{margin-top:9px;background:#f8fafc;border:1px dashed #cbd5e1;border-radius:8px;padding:8px 12px;font-size:13.5px;}
details.fold summary{cursor:pointer;color:#475569;font-weight:600;user-select:none;}
.fold-body{white-space:pre-wrap;line-height:1.75;margin-top:7px;color:#334155;}
mark{background:#fde047;padding:0 2px;border-radius:3px;}
.pager{display:flex;flex-wrap:wrap;gap:6px;align-items:center;justify-content:center;margin:18px 0 8px;}
.pager .pg{padding:6px 11px;border:1px solid var(--line);border-radius:7px;background:#fff;font-size:13px;cursor:pointer;}
.pager .pg:hover:not(:disabled){border-color:var(--accent);color:var(--accent);}
.pager .pg.cur{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:700;}
.pager .pg:disabled{opacity:.4;cursor:default;}
.pager .dots{color:#94a3b8;padding:0 2px;}
.pg-jump,.pg-size{font-size:12.5px;color:var(--sub);display:inline-flex;align-items:center;gap:5px;}
.pg-jump input{width:64px;padding:5px 7px;border:1px solid var(--line);border-radius:6px;}
.pg-size select{padding:5px 7px;border:1px solid var(--line);border-radius:6px;background:#fff;}
#topBtn{position:fixed;right:26px;bottom:30px;width:42px;height:42px;border-radius:50%;border:none;background:var(--accent);color:#fff;font-size:19px;cursor:pointer;box-shadow:0 3px 10px rgba(37,99,235,.4);display:none;}
.foot{max-width:1280px;margin:6px auto 30px;padding:0 16px;font-size:12px;color:#9ca3af;}
@media (max-width:900px){
  .layout{flex-direction:column;padding:10px;}
  aside{width:100%;position:static;max-height:280px;}
}
</style>
</head>
<body>
<header>
  <div class="h-row1">
    <h1>万题库《每日一练》题目查看器</h1>
    <div class="stats" id="statText"></div>
  </div>
  <div class="h-row2">
    <input type="text" id="search" placeholder="搜索题干 / 选项 / 答案 / 解析（多个关键词用空格分隔）">
    <select id="typeSel"></select>
    <select id="subjSel"></select>
    <button id="resetBtn">重置筛选</button>
  </div>
</header>
<div class="layout">
  <aside id="sidebar"></aside>
  <main>
    <div class="list-info" id="listInfo"></div>
    <div id="list"></div>
    <div class="pager" id="pager"></div>
  </main>
</div>
<button id="topBtn" title="回到顶部">↑</button>
<footer class="foot">数据来源：ks.wangxiao.cn 万题库《每日一练》，由课程爬虫项目采集 · 页面生成时间：__TIME__</footer>

<script>
var DATA = /*__DATA__*/null;
var Q = DATA.questions;
var state = {cat:"", exam:"", subj:"", type:"", q:"", page:1, size:30};

/* ---------- 预统计 ---------- */
var cats = {};
Q.forEach(function(x){
  if(!cats[x.c]) cats[x.c] = {total:0, exams:{}, order:[]};
  var c = cats[x.c]; c.total++;
  if(!c.exams[x.e]){ c.exams[x.e] = 0; c.order.push(x.e); }
  c.exams[x.e]++;
});
var typeCount = {};
Q.forEach(function(x){ typeCount[x.t] = (typeCount[x.t]||0) + 1; });
var allSubjects = [];
(function(){ var seen = {}; Q.forEach(function(x){ if(x.s && !seen[x.s]){ seen[x.s]=1; allSubjects.push(x.s); } }); })();
var daySet = {};
Q.forEach(function(x){ daySet[x.d] = 1; });

/* ---------- 工具函数 ---------- */
function esc(s){
  return String(s == null ? "" : s)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
function escRe(s){ return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
function terms(){ return state.q.toLowerCase().split(/\s+/).filter(Boolean); }
function optText(x){
  if(!x.o) return "";
  return x.o.map(function(o){ return o.n + " " + o.c; }).join(" ");
}
function matchQ(x){
  var ts = terms();
  if(!ts.length) return true;
  var hay = (x.q + " " + (x.a||"") + " " + (x.an||"") + " " + (x.m||"") + " " + (x.s||"") + " " + optText(x)).toLowerCase();
  for(var i=0;i<ts.length;i++){ if(hay.indexOf(ts[i]) < 0) return false; }
  return true;
}
function hl(s){
  var e = esc(s);
  var ts = terms();
  if(!ts.length) return e;
  var re = new RegExp("(" + ts.map(function(t){ return escRe(esc(t)); }).join("|") + ")", "gi");
  return e.replace(re, "<mark>$1</mark>");
}
function fmtDay(d){
  return (d && d.length === 8) ? d.slice(0,4)+"-"+d.slice(4,6)+"-"+d.slice(6,8) : d;
}

/* ---------- 筛选与渲染 ---------- */
function filtered(){
  return Q.filter(function(x){
    if(state.cat && x.c !== state.cat) return false;
    if(state.exam && x.e !== state.exam) return false;
    if(state.subj && x.s !== state.subj) return false;
    if(state.type && x.t !== state.type) return false;
    return matchQ(x);
  });
}
function card(x){
  var h = '<div class="q-card">';
  h += '<div class="q-badges">';
  h += '<span class="badge b-type">' + esc(x.t || "未分类") + '</span>';
  h += '<span class="badge">' + esc(x.c) + ' · ' + esc(x.e) + '</span>';
  h += '<span class="badge">科目：' + esc(x.s || "未知") + '</span>';
  h += '<span class="badge">日期：' + fmtDay(x.d) + '</span>';
  h += '<span class="badge">平台序号 ' + x.n + '</span>';
  h += '</div>';
  h += '<div class="q-text">' + hl(x.q) + '</div>';
  if(x.o && x.o.length){
    h += '<div class="opts">';
    for(var i=0;i<x.o.length;i++){
      var o = x.o[i];
      h += '<div class="opt' + (o.r ? " right" : "") + '">' +
           (o.r ? '<span class="tick">✔</span> ' : "") +
           esc(o.n) + ". " + hl(o.c) + '</div>';
    }
    h += '</div>';
  }
  h += '<div class="ans-row">正确答案：' +
       (x.a ? '<span class="ans">' + esc(x.a) + '</span>' : '<span class="ans-none">（见解析）</span>') +
       '</div>';
  if(x.an){
    h += '<details class="fold"' + (x.an.length <= 150 ? " open" : "") +
         '><summary>答案解析</summary><div class="fold-body">' + hl(x.an) + '</div></details>';
  }
  if(x.m){
    h += '<details class="fold"><summary>背景材料（点击展开）</summary>' +
         '<div class="fold-body">' + hl(x.m) + '</div></details>';
  }
  h += '</div>';
  return h;
}
function pageNums(cur, total){
  var out = [];
  if(total <= 9){ for(var i=1;i<=total;i++) out.push(i); return out; }
  out.push(1);
  var s = Math.max(2, cur-2), e = Math.min(total-1, cur+2);
  if(s > 2) out.push("...");
  for(var j=s;j<=e;j++) out.push(j);
  if(e < total-1) out.push("...");
  out.push(total);
  return out;
}
function renderPager(pages, total){
  var el = document.getElementById("pager");
  if(total === 0){ el.innerHTML = ""; return; }
  var h = '<button class="pg" data-p="prev" ' + (state.page <= 1 ? "disabled" : "") + '>« 上一页</button>';
  pageNums(state.page, pages).forEach(function(n){
    if(n === "...") h += '<span class="dots">…</span>';
    else h += '<button class="pg' + (n === state.page ? " cur" : "") + '" data-p="' + n + '">' + n + '</button>';
  });
  h += '<button class="pg" data-p="next" ' + (state.page >= pages ? "disabled" : "") + '>下一页 »</button>';
  h += '<span class="pg-jump">跳至 <input id="jumpInput" type="number" min="1" max="' + pages + '"> 页</span>';
  h += '<span class="pg-size">每页 <select id="sizeSel"><option>20</option><option>30</option><option>50</option><option>100</option></select></span>';
  el.innerHTML = h;
  var ss = document.getElementById("sizeSel");
  ss.value = String(state.size);
  ss.onchange = function(){ state.size = parseInt(ss.value, 10); state.page = 1; render(); };
  var ji = document.getElementById("jumpInput");
  ji.onkeydown = function(ev){
    if(ev.key === "Enter"){
      var v = parseInt(ji.value, 10);
      if(v >= 1 && v <= pages){ state.page = v; render(); window.scrollTo({top:0, behavior:"smooth"}); }
    }
  };
}
function render(){
  var list = filtered();
  var pages = Math.max(1, Math.ceil(list.length / state.size));
  if(state.page > pages) state.page = pages;
  var start = (state.page-1) * state.size;
  var items = list.slice(start, start + state.size);
  document.getElementById("listInfo").textContent =
    "当前筛选：共 " + list.length + " 题 · 第 " + state.page + " / " + pages + " 页";
  document.getElementById("list").innerHTML =
    (items.length ? items.map(card).join("") : '<div class="empty">没有匹配的题目，换个关键词试试</div>');
  renderPager(pages, list.length);
  document.getElementById("topBtn").style.display = window.scrollY > 600 ? "block" : "none";
}

/* ---------- 侧边栏 ---------- */
function buildSidebar(){
  var h = '<div class="sb-item sb-all' + (!state.cat && !state.exam ? " active" : "") +
          '" data-cat="" data-exam="">全部题目 <span class="cnt">' + Q.length + '</span></div>';
  Object.keys(cats).forEach(function(cn){
    var c = cats[cn];
    h += '<div class="sb-item sb-cat' + (state.cat === cn && !state.exam ? " active" : "") +
         '" data-cat="' + esc(cn) + '" data-exam="">' + esc(cn) +
         ' <span class="cnt">' + c.total + '</span></div>';
    c.order.forEach(function(en){
      h += '<div class="sb-item sb-exam' + (state.cat === cn && state.exam === en ? " active" : "") +
           '" data-cat="' + esc(cn) + '" data-exam="' + esc(en) + '">' + esc(en) +
           ' <span class="cnt">' + c.exams[en] + '</span></div>';
    });
  });
  document.getElementById("sidebar").innerHTML = h;
}

/* ---------- 下拉框 ---------- */
function scopeSubjects(){
  var seen = {}, out = [];
  Q.forEach(function(x){
    if(state.cat && x.c !== state.cat) return;
    if(state.exam && x.e !== state.exam) return;
    if(x.s && !seen[x.s]){ seen[x.s] = 1; out.push(x.s); }
  });
  return out;
}
function buildSubjOptions(){
  var list = scopeSubjects();
  if(state.subj && list.indexOf(state.subj) < 0) state.subj = "";
  var sel = document.getElementById("subjSel");
  var h = '<option value="">全部科目（' + list.length + '）</option>';
  list.forEach(function(s){ h += '<option value="' + esc(s) + '">' + esc(s) + '</option>'; });
  sel.innerHTML = h;
  sel.value = state.subj;
}
(function buildTypeOptions(){
  var sel = document.getElementById("typeSel");
  var h = '<option value="">全部题型（' + Object.keys(typeCount).length + '）</option>';
  Object.keys(typeCount).forEach(function(t){
    h += '<option value="' + esc(t) + '">' + esc(t) + '（' + typeCount[t] + '）</option>';
  });
  sel.innerHTML = h;
})();

/* ---------- 事件 ---------- */
var searchTimer = null;
document.getElementById("search").addEventListener("input", function(ev){
  clearTimeout(searchTimer);
  var v = ev.target.value.trim();
  searchTimer = setTimeout(function(){ state.q = v; state.page = 1; render(); }, 250);
});
document.getElementById("typeSel").addEventListener("change", function(ev){
  state.type = ev.target.value; state.page = 1; render();
});
document.getElementById("subjSel").addEventListener("change", function(ev){
  state.subj = ev.target.value; state.page = 1; render();
});
document.getElementById("resetBtn").addEventListener("click", function(){
  state = {cat:"", exam:"", subj:"", type:"", q:"", page:1, size:state.size};
  document.getElementById("search").value = "";
  document.getElementById("typeSel").value = "";
  buildSidebar(); buildSubjOptions(); render();
});
document.getElementById("sidebar").addEventListener("click", function(ev){
  var it = ev.target.closest(".sb-item");
  if(!it) return;
  state.cat = it.getAttribute("data-cat") || "";
  state.exam = it.getAttribute("data-exam") || "";
  state.subj = ""; state.page = 1;
  buildSidebar(); buildSubjOptions(); render();
  window.scrollTo({top:0, behavior:"smooth"});
});
document.getElementById("pager").addEventListener("click", function(ev){
  var b = ev.target.closest("button.pg");
  if(!b || b.disabled) return;
  var p = b.getAttribute("data-p");
  if(p === "prev") state.page = Math.max(1, state.page-1);
  else if(p === "next") state.page = state.page + 1;
  else state.page = parseInt(p, 10);
  render();
  window.scrollTo({top:0, behavior:"smooth"});
});
document.getElementById("topBtn").addEventListener("click", function(){
  window.scrollTo({top:0, behavior:"smooth"});
});
window.addEventListener("scroll", function(){
  document.getElementById("topBtn").style.display = window.scrollY > 600 ? "block" : "none";
});

/* ---------- 初始化 ---------- */
var examTotal = 0;
Object.keys(cats).forEach(function(c){ examTotal += Object.keys(cats[c].exams).length; });
document.getElementById("statText").textContent =
  "共 " + Q.length + " 题 · " + Object.keys(cats).length + " 个一级标题 · " + examTotal +
  " 个二级标题 · " + allSubjects.length + " 个科目 · " + Object.keys(typeCount).length +
  " 种题型 · " + Object.keys(daySet).length + " 个练习日期";
buildSidebar();
buildSubjOptions();
render();
</script>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description="生成题目 HTML 查看器")
    default_out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "ks_questions.html")
    parser.add_argument("--out", default=default_out,
                        help="输出文件名（默认输出到 newcases 目录）")
    args = parser.parse_args()

    conn = pymysql.Connect(autocommit=True,
                           cursorclass=pymysql.cursors.DictCursor, **MYSQL)
    with conn.cursor() as cur:
        cur.execute(SQL)
        rows = cur.fetchall()
    conn.close()

    questions = []
    for r in rows:
        try:
            opts = json.loads(r["options_json"] or "[]")
        except ValueError:
            opts = []
        questions.append({
            "i": r["id"],
            "c": clean(r["category"]), "e": clean(r["exam"]),
            "s": clean(r["subject"]), "d": clean(r["day"]),
            "t": clean(r["question_type"]), "n": int(r["question_no"] or 0),
            "q": clean(r["content"]),
            "o": [{"n": clean(o.get("name")), "c": clean(o.get("content")),
                   "r": int(o.get("isRight") or 0)} for o in opts],
            "a": clean(r["answer"]), "an": clean(r["analysis"]),
            "m": clean(r["material"]),
        })

    data_json = json.dumps({"questions": questions}, ensure_ascii=False,
                           separators=(",", ":")).replace("</", "<\\/")
    page = TEMPLATE.replace("/*__DATA__*/null", data_json)
    page = page.replace("__TIME__", datetime.now().strftime("%Y-%m-%d %H:%M"))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(page)

    size_mb = os.path.getsize(args.out) / 1024.0 / 1024.0
    print("生成完成：%s（%d 道题目，%.1f MB）" % (args.out, len(questions), size_mb))
    print("直接双击该文件即可用浏览器打开查看")


if __name__ == "__main__":
    main()
