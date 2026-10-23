package com.repl.shihuo.security;

import android.os.Process;
import android.util.Log;

/**
 * 对应课件 4.1 节：安全团队把反调试检测写进一个与业务无关的 so。
 *
 * 本类的可删性就是复刻重点：
 *   so 存在  -> nativeCheck() 扫 /proc/self/maps 与线程名，命中 Frida 就杀进程；
 *   so 被删  -> loadLibrary 抛 UnsatisfiedLinkError，被 catch 后检测整体跳过，App 正常运行。
 */
public final class FridaGuard {

    private static final String TAG = "FridaGuard";
    private static final boolean LIB_LOADED;

    static {
        boolean ok;
        try {
            System.loadLibrary("fridadetector");
            ok = true;
        } catch (Throwable t) {
            ok = false;
            Log.w(TAG, "libfridadetector.so 加载失败（可能已被删除）: " + t);
        }
        LIB_LOADED = ok;
        Log.i(TAG, "detector loaded = " + ok);
    }

    private FridaGuard() {
    }

    public static void check() {
        if (!LIB_LOADED) {
            Log.w(TAG, "检测库不存在，反调试检测跳过");
            return;
        }
        boolean hit;
        try {
            hit = nativeCheck();
        } catch (Throwable t) {
            Log.w(TAG, "nativeCheck 异常，跳过", t);
            return;
        }
        if (hit) {
            Log.e(TAG, "检测到 Frida 注入，进程退出（复刻闪退行为）");
            Process.killProcess(Process.myPid());
            System.exit(0);
        } else {
            Log.i(TAG, "未检测到 Frida");
        }
    }

    private static native boolean nativeCheck();
}
