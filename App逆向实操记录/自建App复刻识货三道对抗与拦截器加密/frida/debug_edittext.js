/*
 * debug_edittext.js —— 调试 SocksDroid 弹窗 EditText 的可用方法。
 * 仅限学习研究，禁止商用。
 */
Java.perform(function () {
    Java.choose("android.widget.EditText", {
        onMatch: function (inst) {
            if (!inst.isShown()) {
                return;
            }
            console.log("[*] class=" + inst.getClass().getName());
            var ovs = inst.setText.overloads;
            console.log("[*] setText overloads=" + ovs.length);
            ovs.forEach(function (o) {
                console.log("    " + o.argumentTypes.join(","));
            });
            var text = inst.getText();
            console.log("[*] getText class=" + text.getClass().getName());
            try {
                var Editable = Java.use("android.text.Editable");
                var ed = Java.cast(text, Editable);
                console.log("[*] cast ok, replace type=" + typeof ed.replace);
            } catch (e) {
                console.log("[!] cast 失败: " + e);
            }
        },
        onComplete: function () {}
    });
});
