/*
 * set_socks_ip.js —— 用 Frida 给 SocksDroid 的 Server IP 输入框赋值。
 *
 * 背景：SocksDroid 每次启动都会把 server_ip 重置成 127.0.0.1，直接改
 * /data/data/net.typeblog.socks/shared_prefs/*.xml 会在启动时被覆盖；
 * 而 adb input text 在中文输入法下会把 "." 变成 "。"，没法输入 IP。
 * 这里 attach 到已运行的 SocksDroid，直接对弹窗里的 EditText 调 setText，
 * 等价于用户手输，之后点"确定"由 App 自己保存。
 *
 * 用法：python driver.py attach set_socks_ip.js 6 net.typeblog.socks
 * 仅限学习研究，禁止商用。
 */
Java.perform(function () {
    var IP = "192.168.31.220";
    var found = false;
    var JString = Java.use("java.lang.String");
    Java.choose("android.widget.EditText", {
        onMatch: function (inst) {
            try {
                if (!inst.isShown()) {
                    return;
                }
                console.log("[*] 命中可见的 EditText");
                found = true;
                Java.scheduleOnMainThread(function () {
                    try {
                        // 这个 App 的 TextView 只暴露了 setText(CharSequence, BufferType) 一个重载
                        var BufferType = Java.use("android.widget.TextView$BufferType");
                        inst.setText.overload("java.lang.CharSequence", "android.widget.TextView$BufferType")
                            .call(inst, JString.$new(IP), BufferType.EDITABLE.value);
                        console.log("[*] 已写入 " + IP);
                    } catch (e) {
                        console.log("[!] setText 失败: " + e);
                    }
                });
            } catch (e) {
                console.log("[!] 读取 EditText 失败: " + e);
            }
        },
        onComplete: function () {
            if (!found) {
                console.log("[!] 没有找到 EditText，请先打开 Server IP 弹窗");
            }
        }
    });
});
