# -*- coding: utf-8 -*-
"""
01：课件「eval 函数」案例重写（Python 侧）
================================================
对应课件：Day25 代码/01 eval函数.py

课件原版：已验证 eval 可以把字符串当代码执行。
本重写版补充三个实战关注点：
  1. eval 与直接执行的等价性（同一表达式）
  2. eval 的作用域行为：默认用当前 globals/locals（这是"混淆代码能在正确上下文中求值"的根基）
  3. 动态代码在逆向中的意义：字符串代码不参与静态关键字搜索，但运行时必然现形

仅本地计算，无任何网络请求。
"""
import math

print("=" * 64)
print("01 eval 函数验证（Python 侧）")
print("=" * 64)

# ---------- 1. 课件同款表达式：字符串 vs eval ----------
exp = "1 + 2 * 3 / 4 + (5 ** 2 - 8)"
print("\n[1] 课件表达式 %r" % exp)
print("    直接打印            :", exp)
print("    eval(exp)           :", eval(exp))
assert eval(exp) == 1 + 2 * 3 / 4 + (5 ** 2 - 8) == 19.5
print("    [PASS] eval 结果与直接求值一致 == 19.5")

# ---------- 2. eval 的作用域行为 ----------
print("\n[2] 作用域行为：eval 默认使用调用处的 globals/locals")
x = 10
y = 20
scope_res = eval("x * y + math.sqrt(16)")   # 能访问当前作用域的 x/y 和导入的 math
print("    eval('x * y + math.sqrt(16)') =", scope_res)
assert scope_res == 204
print("    [PASS] eval 可见当前作用域变量与模块 —— 这就是混淆代码能跑通的原因")

# Python 知识点：Python 的 eval 只能求值表达式，赋值语句要用 exec
# （对比：JS 的 eval 表达式和语句都能执行，见 JS 侧验证）
exec("q = x * 2")
print("    exec('q = x * 2') 后 q =", q)
assert q == 20
print("    [PASS] Python 分工：eval=表达式求值 / exec=语句执行")

# ---------- 3. 逆向视角：字符串代码对静态搜索隐身 ----------
print("\n[3] 逆向视角：字符串形式的代码对'明文搜索'隐身")
hidden = "sum([i * i for i in range(5)])"     # 搜 "sum" 能找到，但搜不到执行结构
print("    源码中的字符串     :", repr(hidden))
print("    运行时实际结果     :", eval(hidden), "（0^2+1^2+2^2+3^2+4^2）")
assert eval(hidden) == 30
print("    [PASS] 静态看只是数据，动态求值才现形 —— 对应 JS 侧 hook eval 的动机")

print("\n结论：eval 是'代码即数据'的入口；JS 逆向中网站用它藏算法，")
print("      对付它的手段是在 eval/Function 处下 hook 打印入参（见 JS 侧验证与 Playwright 实战）。")
print("=" * 64)
print("ALL PASS")
