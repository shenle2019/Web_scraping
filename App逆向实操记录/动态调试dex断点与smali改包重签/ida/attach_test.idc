#include <idc.idc>
// 仅限学习研究，禁止商用。
// 最小连通性测试：加载 android 调试器 -> 连接 android_server -> attach 进程 -> 取 PC

static main() {
    auto ok, ev, pid;
    pid = 31972;
    Message("=== idc start ===\n");
    ok = LoadDebugger("android", 0);
    Message("LoadDebugger=%d\n", ok);
    ok = SetRemoteDebugger("127.0.0.1", "", 23946);
    Message("SetRemoteDebugger=%d\n", ok);
    ok = AttachProcess(pid, -1);
    Message("AttachProcess=%d\n", ok);
    ev = GetDebuggerEvent(WFNE_SUSP, 30000);
    Message("event=%d\n", ev);
    Message("PC=0x%x\n", GetRegValue("PC"));
    Exit(0);
}
