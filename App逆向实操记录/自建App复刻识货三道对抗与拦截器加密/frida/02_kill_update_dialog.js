/*
 * 02_kill_update_dialog.js —— 复刻课件 3.3 节：Hook UpdateDialog.show 干掉强制更新弹窗。
 *
 * 用法（App 已启动）：frida -U -n 识货复刻 -l 02_kill_update_dialog.js
 * 用法（spawn）：frida -U -f com.repl.shihuo -l 02_kill_update_dialog.js
 * 预期：日志出现"被拦截，不弹窗"，界面上不再出现 7.73.0 更新框，业务按钮可直接点。
 * 仅限学习研究，禁止商用。
 */
Java.perform(function () {
    var Dialog = Java.use("com.repl.shihuo.update.UpdateDialog");
    Dialog.show.implementation = function (activity, latest) {
        console.log("[hook] UpdateDialog.show(" + latest + ") 被拦截，未弹窗");
    };
    console.log("[*] 已 Hook com.repl.shihuo.update.UpdateDialog.show");
});
