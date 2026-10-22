package com.autohome.chezhiying;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * 键值缓存，对应真实 App 里的 SPUtils：
 * imei 首次取到后落盘，deviceId 由服务端下发后落盘。
 */
public class SPUtils {

    private static final String SP_NAME = "chezhiying_sp";

    private static SharedPreferences sp(Context context) {
        return context.getApplicationContext()
                .getSharedPreferences(SP_NAME, Context.MODE_PRIVATE);
    }

    public static String getIMEI(Context context) {
        return sp(context).getString("imei", "");
    }

    public static void saveIMEI(Context context, String imei) {
        sp(context).edit().putString("imei", imei).apply();
    }

    public static String getDeviceId(Context context) {
        return sp(context).getString("deviceid", "");
    }

    public static void saveDeviceId(Context context, String deviceId) {
        sp(context).edit().putString("deviceid", deviceId).apply();
    }
}
