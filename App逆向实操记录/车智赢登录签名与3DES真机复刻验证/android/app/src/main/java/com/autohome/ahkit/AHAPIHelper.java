package com.autohome.ahkit;

import android.content.Context;
import android.util.Log;

import com.autohome.ahkit.utils.SecurityUtil;

import java.util.TreeMap;

/**
 * 复刻自车智赢的 AHAPIHelper。
 * 真实 App 里 getDesKey 会走到 so 里取值，这里用常量代替（本机没有 NDK）。
 * toSign 是历史遗留的旧签名入口，登录链路并不走它——保留它是为了让
 * “关键字搜索先搜到错的候选”这个场景可以被真实复现。
 */
public class AHAPIHelper {

    private static final String TAG = "CheZhiYing";
    static final String DES3_KEY = "appapiche168comappapiche168comap";

    public static String getDesKey(Context context) {
        String key = com.autohome.ahkit.jni.CheckSignUtil.get3desKey();
        Log.i(TAG, "getDesKey -> " + key);
        return key;
    }

    /** 旧版无盐签名，登录不调用 */
    public static String toSign(Context context, TreeMap<String, String> params) {
        StringBuilder sb = new StringBuilder();
        for (String key : params.keySet()) {
            sb.append(key).append(params.get(key));
        }
        return SecurityUtil.encodeMD5(sb.toString()).toUpperCase();
    }
}
