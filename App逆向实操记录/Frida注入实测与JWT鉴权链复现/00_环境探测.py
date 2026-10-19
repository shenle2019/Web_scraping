# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""环境探测：确认电脑端 frida、手机端 frida-server、adb 转发与远程设备连通性。

对应课件 day04 的 0-端口转发.py / 1-打印手机正在运行app.py，
这里整合成一个自检脚本，作为实操记录的第一步。
"""
import platform
import subprocess
import sys

frida_server_bin = "fs1663"  # 手机端部署后的文件名，可按需修改


def run(cmd):
    """执行系统命令并返回合并后的输出文本。"""
    try:
        out = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
        text = (out.stdout + out.stderr).decode("utf-8", "ignore").strip()
        return text
    except Exception as exc:
        return "[执行失败] %s" % exc


def main():
    print("=== 1. 电脑环境 ===")
    print("OS:", platform.platform())
    print("Python:", sys.version.split()[0])
    try:
        import frida
        print("frida (PC):", frida.__version__)
    except Exception as exc:
        print("frida 未安装:", exc)
        return

    print("\n=== 2. adb 与手机连接 ===")
    print(run("adb devices"))
    print("手机 CPU 架构:", run("adb shell getprop ro.product.cpu.abi"))

    print("\n=== 3. 手机端 frida-server 进程 ===")
    ps_out = run('adb shell "ps -A"')
    hits = [line for line in ps_out.splitlines() if frida_server_bin in line or "frida" in line.lower()]
    print("\n".join(hits) if hits else "[未发现 frida-server 进程，请先启动]")

    print("\n=== 4. 端口转发 ===")
    print(run("adb forward --list"))

    print("\n=== 5. frida 远程设备连通性 ===")
    try:
        rdev = frida.get_remote_device()
        print("device:", rdev)
        procs = rdev.enumerate_processes()
        print("进程总数:", len(procs))
        front = rdev.get_frontmost_application()
        print("前台应用:", front)
    except Exception as exc:
        print("[连通失败] %s" % exc)


if __name__ == "__main__":
    main()
