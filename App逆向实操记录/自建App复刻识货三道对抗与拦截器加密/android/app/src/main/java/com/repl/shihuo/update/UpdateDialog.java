package com.repl.shihuo.update;

import android.app.Activity;
import android.app.AlertDialog;

import com.repl.shihuo.BuildConfig;

/**
 * 复刻课件 3.3 节的强制更新弹窗。
 * 不可取消、只有"立即更新"一个按钮；Frida 脚本 Hook 的就是 show(Activity, String)。
 */
public final class UpdateDialog {

    private UpdateDialog() {
    }

    public static void show(Activity activity, String latest) {
        new AlertDialog.Builder(activity)
                .setTitle("发现新版本 " + latest)
                .setMessage("当前版本 " + BuildConfig.VERSION_NAME
                        + " 已停止维护，请升级后继续使用。")
                .setCancelable(false)
                .setPositiveButton("立即更新", (dialog, which) -> {
                    // 演示用，不做实际下载
                })
                .show();
    }
}
