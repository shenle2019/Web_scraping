/*
 * 06_shihuo_dialog_show_then_dismiss.js —— 更新弹窗的第二种绕过思路。
 *
 * 背景：实测直接 return 不调用 show()，识货会在约 14 秒后自行结束进程（疑似更新看门狗）。
 * 思路：让弹窗正常 show（满足生命周期），800ms 后自动 dismiss，等效于用户看到后秒关。
 *
 * 用法：python driver.py spawn 06_shihuo_dialog_show_then_dismiss.js 35 com.hupu.shihuo
 * 仅限学习研究，禁止商用。
 */
Java.perform(function () {
    var TARGET = "com.shizhi.shihuoapp.component.dialogqueue.dialog.UpdateDialog";
    var Dialog = Java.use("android.app.Dialog");
    Dialog.show.implementation = function () {
        var name = "unknown";
        try {
            name = this.getClass().getName();
        } catch (e) {
            // ignore
        }
        if (name === TARGET) {
            console.log("[hook] 命中更新弹窗，先 show 再定时 dismiss");
            this.show.overload().call(this);
            var self = this;
            setTimeout(function () {
                Java.perform(function () {
                    try {
                        self.dismiss();
                        console.log("[hook] 更新弹窗已自动 dismiss");
                    } catch (e) {
                        console.log("[hook] dismiss 失败: " + e);
                    }
                });
            }, 800);
            return;
        }
        return this.show.overload().call(this);
    };
    console.log("[*] 已挂 show-then-dismiss，目标 " + TARGET);
});
