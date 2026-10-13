# -*- coding: utf-8 -*-
"""
23：无限 debugger 对抗验证（CDP 对照实验）
=========================================================
对应课件：07 无限debugger.js（六种写法、反调试原理）
本脚本用 Chrome DevTools Protocol（CDP Debugger 域）做"真断点"对照实验：

  场景 A（不注入对抗）：
      CDP 打开 Debugger 域 → 页面每触发一次 debugger 语句就产生一次
      "Debugger.paused"（真实断点，无自动恢复则页面永久卡死）
      → 统计 3 秒观察窗内的暂停次数（证明无限断点确实在拖住页面）

  场景 B（注入 hook_scripts/anti_debugger.js）：
      同样的观察窗口内 paused == 0，且：
        - __antiStats.intervalBlocked >= 1（链1 定时器回调被掐断）
        - __antiStats.functionBlocked >= 1（链2 构造器被去势）
        - 页面数据正常渲染（功能无损）
      → 证明"源头切断"策略生效

  说明：无调试器挂载时 debugger 是空操作；本实验通过 CDP 挂载调试器，
        真实复现了"无限断点拖住分析者"的场景与对抗效果。
"""
import asyncio
import os
import sys

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from playwright.async_api import async_playwright
import pw_common as C

OBSERVE_SECONDS = 3.0


async def run_scenario(p, use_anti):
    """返回 {paused, stats, tick, items}；use_anti=True 时先注入对抗脚本"""
    browser = await p.chromium.launch(channel="msedge", headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    if use_anti:
        await page.add_init_script(path=os.path.join(C.BASE, "hook_scripts/anti_debugger.js"))

    cdp = await context.new_cdp_session(page)
    paused_events = []

    async def resume_soon():
        try:
            await cdp.send("Debugger.resume")
        except Exception:
            pass

    def on_paused(params):
        paused_events.append(params)
        asyncio.ensure_future(resume_soon())   # 立即恢复，避免页面永久卡死

    cdp.on("Debugger.paused", on_paused)
    await cdp.send("Debugger.enable")

    await page.goto(C.URL_HOME, wait_until="domcontentloaded")
    await asyncio.sleep(OBSERVE_SECONDS)       # 观察窗口：数暂停次数

    await cdp.send("Debugger.disable")         # 停止断点，避免采集数据时被卡
    await asyncio.sleep(0.3)

    stats = await page.evaluate("window.__antiStats || null")
    tick = await page.evaluate("window.__dbgTick || 0")
    items = await page.locator("#goods-list li").count()

    await browser.close()
    return {"paused": len(paused_events), "stats": stats, "tick": tick, "items": items}


async def main():
    C.hr("23 无限 debugger 对抗验证（CDP 对照实验，观察窗口 %.0f 秒）" % OBSERVE_SECONDS)

    with C.LocalSite():
        async with async_playwright() as p:
            print("\n----- 场景 A：不注入对抗（CDP 挂载调试器 = 真实断点） -----")
            ra = await run_scenario(p, use_anti=False)
            print("  paused 暂停次数 : %d" % ra["paused"])
            print("  页面 __dbgTick  : %d" % ra["tick"])
            print("  商品渲染条数    : %d" % ra["items"])

            print("\n----- 场景 B：注入 anti_debugger.js（源头切断） -----")
            rb = await run_scenario(p, use_anti=True)
            print("  paused 暂停次数 : %d" % rb["paused"])
            print("  对抗留痕        : %s" % rb["stats"])
            print("  页面 __dbgTick  : %d（链2 循环仍存活）" % rb["tick"])
            print("  商品渲染条数    : %d" % rb["items"])

    print("\n----- 结论断言 -----")
    ok = True
    ok &= C.check("场景A：出现了真实断点暂停（>=3 次，证明无限 debugger 在拖住页面）", ra["paused"] >= 3)
    ok &= C.check("场景A：页面本身功能正常（数据渲染 12 条）", ra["items"] == 12)
    ok &= C.check("场景B：注入对抗后暂停次数为 0（断点被源头切断）", rb["paused"] == 0)
    stats = rb["stats"] or {}
    ok &= C.check("场景B：链1 定时器回调被掐断留痕（intervalBlocked >= 1）",
                  stats.get("intervalBlocked", 0) >= 1)
    ok &= C.check("场景B：链2 构造器被去势留痕（functionBlocked >= 1）",
                  stats.get("functionBlocked", 0) >= 1)
    ok &= C.check("场景B：页面功能无损（链2 循环仍存活且 12 条数据渲染）",
                  rb["tick"] >= 2 and rb["items"] == 12)

    C.hr("23 结论: " + ("全部通过 —— 无限断点被有效对抗，页面功能保持完整" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
