package com.autohome.chezhiying;

import android.util.Log;

import com.autohome.ahkit.utils.SecurityUtil;

import java.util.Locale;
import java.util.TreeMap;

/**
 * 复刻自车智赢的 SignManager：TreeMap 按 key 排序 -> key+value 无分隔符拼接
 * -> 前后各加一次盐 -> MD5 -> 大写。
 */
public class SignManager {

    private static final String TAG = "CheZhiYing";

    public static final SignManager INSTANCE = new SignManager();

    private static final String KEY_V1 = "a1b2c3d4e5f6g7h8";
    private static final String KEY_V2 = "W@oC!AH_6Ew1f6%8";
    private static final String KEY_SHARE = "share#2024$chezhiying";
    private static final String KEY_AUTOHOME = "autohome@api#2024";

    public String signByType(int type, TreeMap<String, String> params) {
        String salt;
        switch (type) {
            case 1:
                salt = KEY_V2;
                break;
            case 2:
                salt = KEY_SHARE;
                break;
            case 3:
                salt = KEY_AUTOHOME;
                break;
            default:
                salt = KEY_V1;
                break;
        }
        StringBuilder sb = new StringBuilder();
        sb.append(salt);
        for (String key : params.keySet()) {
            sb.append(key).append(params.get(key));
        }
        sb.append(salt);
        String sign = SecurityUtil.encodeMD5(sb.toString()).toUpperCase(Locale.ROOT);
        Log.i(TAG, "signByType type=" + type + " salt=" + salt + " raw=" + sb);
        return sign;
    }
}
