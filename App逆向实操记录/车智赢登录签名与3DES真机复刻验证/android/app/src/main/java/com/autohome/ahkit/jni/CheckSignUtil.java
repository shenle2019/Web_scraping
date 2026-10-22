package com.autohome.ahkit.jni;

/**
 * 复刻自车智赢的 com.autohome.ahkit.jni.CheckSignUtil。
 * 真实 App 里 get3desKey 是 native 方法，key 常量在下发的 .so 的 .rodata 里；
 * 本机未装 NDK，这里用同样的常量模拟“从 native 层取 key”，
 * 尾部的包名校验沿用真实实现的“首次校验后缓存”形态。
 */
public class CheckSignUtil {

    private static final String DES3_KEY = "appapiche168comappapiche168comap";
    private static String checkState = "";

    public static String get3desKey() {
        if (!checkState.contains("yes")) {
            checkState = checkPackage() ? "yes" : "no";
        }
        return DES3_KEY;
    }

    private static boolean checkPackage() {
        // 真实 App 在这里做包名/签名校验，复刻版固定通过
        return true;
    }
}
