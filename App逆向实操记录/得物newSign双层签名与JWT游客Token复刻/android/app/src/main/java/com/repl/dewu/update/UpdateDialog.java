package com.repl.dewu.update;

import android.app.Activity;
import android.app.AlertDialog;

import com.repl.dewu.net.Api;

public class UpdateDialog {

    /** 不可取消的强制更新弹窗，复刻课件里的更新拦截点 */
    public static void show(Activity activity, String latest) {
        if (activity.isFinishing()) {
            return;
        }
        new AlertDialog.Builder(activity)
                .setTitle("发现新版本 " + latest)
                .setMessage("当前版本 " + Api.VERSION + "，需要升级后才能继续使用。")
                .setCancelable(false)
                .setPositiveButton("立即更新", (dialog, which) -> activity.finish())
                .show();
    }
}
