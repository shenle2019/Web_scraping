package com.shenjiahang.netapp.util;

import android.content.Context;
import android.content.SharedPreferences;
import android.text.TextUtils;

import com.shenjiahang.netapp.net.NetConfig;

/**
 * token 落盘：SharedPreferences 明文 + MODE_PRIVATE。
 * root 后直接 adb cat 就能读到，这正是逆向时最省事的突破点。
 */
public final class AppPrefs {

    private AppPrefs() {
    }

    private static SharedPreferences sp(Context ctx) {
        return ctx.getSharedPreferences(NetConfig.SP_NAME, Context.MODE_PRIVATE);
    }

    public static void saveLogin(Context ctx, String user, String token) {
        sp(ctx).edit()
                .putString(NetConfig.SP_KEY_USER, user)
                .putString(NetConfig.SP_KEY_TOKEN, token)
                .apply();
    }

    public static String getToken(Context ctx) {
        return sp(ctx).getString(NetConfig.SP_KEY_TOKEN, "");
    }

    public static String getUser(Context ctx) {
        return sp(ctx).getString(NetConfig.SP_KEY_USER, "");
    }

    public static void clear(Context ctx) {
        sp(ctx).edit().clear().apply();
    }

    public static boolean hasToken(Context ctx) {
        return !TextUtils.isEmpty(getToken(ctx));
    }
}
