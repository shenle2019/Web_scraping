# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

day30 dex 动态调试复刻（SoDebug 自建 App）：
  1) adb shell am start -D 让 App 以"等待调试器"方式启动
  2) adb forward tcp:8700 jdwp:<pid>（等价于 DDMS 做的事）
  3) jdb 附加，在 com.nb.sodebug.MainActivity$1.onClick 下断点
  4) cont 放行 -> adb 点击"点我" -> 断点命中
  5) next 单步越过 Utils.demo() 这行 -> locals 看 result=3
  6) cont 继续 -> logcat 里应出现 "测试: 3"

只用课件自带的 SoDebug 测试 App，不涉及任何线上账号。

用法：python 01_dex_debug.py [--out evidence_01_dex_debug.log]
"""
import argparse
import io
import os
import queue
import re
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET

PKG = "com.nb.sodebug"
ACT = "com.nb.sodebug/com.nb.sodebug.MainActivity"
BREAK_CLASS = "com.nb.sodebug.MainActivity$1"
BREAK_METHOD = "onClick"
JDB = r"C:\Program Files\Java\jdk-1.8\bin\jdb.exe"
TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tmp")
LOGS = []


def log(line=""):
    line = line if isinstance(line, str) else str(line)
    print(line)
    LOGS.append(line)


def adb(args, timeout=60):
    p = subprocess.run(["adb"] + args, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return (p.stdout or "") + (p.stderr or "")


def adb_bin(args, timeout=60):
    return subprocess.run(["adb"] + args, capture_output=True, timeout=timeout)


def wait_pid(timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        out = adb(["shell", "pidof", PKG]).strip()
        if out:
            return out.split()[0]
        time.sleep(0.5)
    return ""


def tap_by_text(text):
    """uiautomator dump 拿到控件坐标后点击。"""
    for _ in range(3):
        adb(["shell", "uiautomator", "dump", "/sdcard/ui_dex.xml"])
        local = os.path.join(TMP, "ui_dex.xml")
        log(adb(["pull", "/sdcard/ui_dex.xml", local]).strip())
        try:
            tree = ET.parse(local)
        except Exception as exc:
            log("[tap] dump 解析失败：%s" % exc)
            time.sleep(1)
            continue
        for node in tree.iter("node"):
            if node.get("text") == text:
                x1, y1, x2, y2 = map(int, re.findall(r"\d+", node.get("bounds")))
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                log("[tap] 找到 \"%s\" bounds=(%d,%d,%d,%d) -> 点击 (%d,%d)"
                    % (text, x1, y1, x2, y2, cx, cy))
                adb(["shell", "input", "tap", str(cx), str(cy)])
                return True
        time.sleep(1)
    return False


class Jdb(object):
    def __init__(self):
        # jdb 在中文 Windows 上输出 GBK（jdb 的本地化消息也是中文），按 gbk 解码
        self.proc = subprocess.Popen(
            [JDB, "-connect", "com.sun.jdi.SocketAttach:hostname=127.0.0.1,port=8700"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="gbk", errors="replace", bufsize=1)
        self.q = queue.Queue()
        self.buf = []
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        for line in self.proc.stdout:
            self.q.put(line.rstrip("\r\n"))

    def send(self, cmd):
        log("[jdb>] %s" % cmd)
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()

    def drain(self, timeout=3.0):
        end = time.time() + timeout
        got = []
        while time.time() < end:
            try:
                line = self.q.get(timeout=0.2)
            except queue.Empty:
                continue
            got.append(line)
            self.buf.append(line)
            log("[jdb] " + line)
        return got

    def wait_for(self, pattern, timeout=30.0):
        rx = re.compile(pattern)
        end = time.time() + timeout
        hit = []
        while time.time() < end:
            try:
                line = self.q.get(timeout=0.3)
            except queue.Empty:
                continue
            self.buf.append(line)
            log("[jdb] " + line)
            hit.append(line)
            if rx.search(line):
                return True, hit
        return False, hit

    def close(self):
        try:
            self.send("exit")
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="evidence_01_dex_debug.log")
    args = ap.parse_args()
    os.makedirs(TMP, exist_ok=True)
    verdict = {}

    log("== 步骤 0：检查设备与安装状态 ==")
    log(adb(["devices"]).strip())
    log("[0] ro.debuggable = %s" % adb(["shell", "getprop", "ro.debuggable"]).strip())
    log("[0] run-as 验证 debuggable = %s" % adb(["shell", "run-as", PKG, "id"]).strip())
    log("[0] 包路径 = %s" % adb(["shell", "pm", "path", PKG]).strip())
    verdict["app_debuggable"] = "uid=" in adb(["shell", "run-as", PKG, "id"])

    log("")
    log("== 步骤 1：am start -D 以调试模式启动 ==")
    adb(["shell", "am", "force-stop", PKG])
    adb(["forward", "--remove-all"])
    adb(["logcat", "-c"])
    log(adb(["shell", "am", "start", "-D", "-n", ACT]).strip())
    pid = wait_pid()
    log("[1] 进程 pid = %s" % pid)
    verdict["started_waiting_debugger"] = bool(pid)
    if not pid:
        log("[!] 进程没起来，退出")
        return finish(args, verdict)

    log("")
    log("== 步骤 2：端口转发 tcp:8700 -> jdwp:%s ==" % pid)
    log(adb(["forward", "tcp:8700", "jdwp:%s" % pid]).strip())
    log(adb(["forward", "--list"]).strip())

    log("")
    log("== 步骤 3：jdb 附加 ==")
    jdb = Jdb()
    # jdb 的提示符 ">" 不带换行，按行读不到，这里用"初始化完成 + 稳定输出"判定附加成功
    init, _ = jdb.wait_for(r"(正在初始化jdb|Initializing jdb)", timeout=40)
    time.sleep(2)
    jdb.drain(2)
    alive = init and jdb.proc.poll() is None
    verdict["jdb_attached"] = alive
    if not alive:
        log("[!] jdb 附加失败")
        jdb.close()
        return finish(args, verdict)

    log("")
    log("== 步骤 4：下断点并放行 ==")
    jdb.send("stop in %s.%s" % (BREAK_CLASS, BREAK_METHOD))
    jdb.drain(3)
    jdb.send("cont")
    time.sleep(3)

    log("")
    log("== 步骤 5：点击按钮触发断点 ==")
    verdict["tapped"] = tap_by_text("点我")
    hit, lines = jdb.wait_for(r"(Breakpoint hit|断点命中)", timeout=30)
    verdict["breakpoint_hit"] = hit
    if hit:
        jdb.drain(2)
        log("")
        log("== 步骤 6：next 单步越过 Utils.demo()，看局部变量 ==")
        jdb.send("next")
        jdb.drain(4)
        jdb.send("locals")
        locals_lines = jdb.drain(4)
        joined = "\n".join(locals_lines)
        log("[6] locals 里是否出现 result = 3：%s" % ("result = 3" in joined))
        verdict["locals_result_3"] = "result = 3" in joined
        jdb.send("cont")
        jdb.drain(2)
    jdb.close()

    log("")
    log("== 步骤 7：logcat 验证 native 返回 3 ==")
    time.sleep(2)
    cat = adb(["logcat", "-d", "-v", "brief"])
    app_lines = [ln for ln in cat.splitlines() if "测试" in ln or "sodebug" in ln.lower()]
    for ln in app_lines[-10:]:
        log("[logcat] " + ln)
    verdict["logcat_result_3"] = any("测试" in ln and "3" in ln for ln in app_lines)

    log("")
    log("== 判定 ==")
    for k, v in verdict.items():
        log("  %-28s %s" % (k, "PASS" if v else "FAIL"))
    all_ok = all(verdict.values())
    log("总判定：%s" % ("PASS" if all_ok else "FAIL"))
    return finish(args, verdict)


def finish(args, verdict):
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(LOGS) + "\n")
        print("已写入 %s" % os.path.abspath(args.out))
    return 0 if all(verdict.values()) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
