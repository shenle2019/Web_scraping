/*
 * 01_trace_dlopen.js —— 复刻课件 4.2 节：Hook dlopen / android_dlopen_ext 打印 App 加载的所有 so。
 *
 * 用法：frida -U -f com.repl.shihuo -l 01_trace_dlopen.js --no-pause
 * 预期：so 列表刷到最后一个 libfridadetector.so 后进程被杀（检测命中）。
 * 仅限学习研究，禁止商用。
 */
function emit(line) {
    console.log("[dlopen] " + line);
}

function hook(name) {
    var addr = Module.findExportByName(null, name);
    if (addr === null) {
        console.log("[!] 找不到导出函数 " + name);
        return;
    }
    Interceptor.attach(addr, {
        onEnter: function (args) {
            try {
                emit(Memory.readCString(args[0]));
            } catch (e) {
                emit("<读取失败 " + e + ">");
            }
        }
    });
    console.log("[*] 已 Hook " + name);
}

hook("dlopen");
hook("android_dlopen_ext");

console.log("[*] 开始记录 so 加载顺序，若出现 frida 字样说明注入已被发现");
