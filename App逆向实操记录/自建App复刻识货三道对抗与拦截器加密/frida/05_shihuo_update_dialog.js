/*
 * 05_shihuo_update_dialog.js —— 复刻课件 3.3 节，作用在真实识货 7.20.1 上。
 *
 * 实测结论（本机 7.20.1 / versionCode 15670）：
 *   搜索"新版本"能搜到 com.azhon.appupdate.dialog.UpdateDialog，但真正弹出来的是
 *   com.shizhi.shihuoapp.component.dialogqueue.dialog.UpdateDialog（两者都叫 UpdateDialog）。
 *   所以只 Hook azhon 那个类不会生效，必须按运行期打印出来的真实类名拦截。
 *
 * 做法：Hook android.app.Dialog.show()，命中 dialogqueue.dialog.UpdateDialog 就不调用原方法，
 * 其余 Dialog 正常放行。
 *
 * 用法：python driver.py spawn 05_shihuo_update_dialog.js 25 com.hupu.shihuo
 * 前置：已删除 libmsaoaidsec.so，否则 spawn 阶段就被反调试杀掉。
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
            console.log("[hook] 拦截真实更新弹窗 " + name);
            return;
        }
        console.log("[dialog] " + name);
        return this.show.overload().call(this);
    };
    console.log("[*] 已 Hook android.app.Dialog.show，目标类 " + TARGET);
});
