package com.autohome.ahkit;

import android.content.Context;
import android.text.TextUtils;
import com.autohome.ahkit.jni.CheckSignUtil;
import com.autohome.ahkit.utils.AHAppInfoUtil;
import com.autohome.ahkit.utils.AHDeviceUtil;
import com.autohome.ahkit.utils.SecurityUtil;
import com.autohome.ahkit.utils.UserInfoUtil;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Arrays;
import java.util.Map;
import java.util.TreeMap;
/* loaded from: E:\路飞学城\课件\APP逆向(12期)\_repl_day14_chezhiying\apk_unpack\dex\classes.dex */
public class AHAPIHelper {
    public static final String APP_ID = "2scapp.android";
    private static final String PARAM_APPID = "_appid";
    private static final String PARAM_APPVERSION = "appversion";
    private static final String PARAM_CHANNELID = "channelid";
    private static final String PARAM_SIGN = "_sign";
    private static final String PARAM_UDID = "udid";
    private static final String PARAM_USERKEY = "userkey";
    public static final String[] URL_FILTER_USEDKEY_UDID = {"apirnappusc.che168.com"};
    private static String mSignKey = "";
    private static String mDesKey = "";

    public static String getDesKey(Context context) {
        if (TextUtils.isEmpty(mDesKey)) {
            getSignDesKey(context);
        }
        return mDesKey;
    }

    public static String getSignKey(Context context) {
        if (TextUtils.isEmpty(mSignKey)) {
            getSignDesKey(context);
        }
        return mSignKey;
    }

    private static void getSignDesKey(Context context) {
        mDesKey = CheckSignUtil.get3desKey(context);
    }

    public static TreeMap<String, String> toSigndMap(Context context, TreeMap<String, String> treeMap) {
        if (treeMap == null) {
            return null;
        }
        appendPublicParam(context, treeMap);
        appendUserKey(context, treeMap);
        appendUdid(context, treeMap);
        treeMap.put(PARAM_SIGN, toSign(context, treeMap));
        return treeMap;
    }

    public static TreeMap<String, String> toSigndMap(Context context, TreeMap<String, String> treeMap, String str) {
        if (treeMap == null) {
            return null;
        }
        appendPublicParam(context, treeMap);
        if (isAddUsedkeyAndUdid(str)) {
            appendUserKey(context, treeMap);
            appendUdid(context, treeMap);
        }
        treeMap.put(PARAM_SIGN, toSign(context, treeMap));
        return treeMap;
    }

    public static boolean isAddUsedkeyAndUdid(String str) {
        if (TextUtils.isEmpty(str)) {
            return true;
        }
        try {
            String host = new URL(str).getHost();
            if (TextUtils.isEmpty(host)) {
                return true;
            }
            return !Arrays.asList(URL_FILTER_USEDKEY_UDID).contains(host);
        } catch (MalformedURLException unused) {
            return true;
        }
    }

    public static TreeMap<String, String> toSignedMap(Context context, boolean z, TreeMap<String, String> treeMap) {
        if (treeMap == null) {
            return null;
        }
        appendPublicParam(context, treeMap);
        if (z) {
            appendUdid(context, treeMap);
        }
        treeMap.put(PARAM_SIGN, toSign(context, treeMap));
        return treeMap;
    }

    private static void appendPublicParam(Context context, Map<String, String> map) {
        map.put(PARAM_APPID, APP_ID);
        map.put("channelid", AHAppInfoUtil.getUMSChannelId(context));
        map.put(PARAM_APPVERSION, AHAppInfoUtil.getAppVersionName(context));
    }

    public static void appendUdid(Context context, Map<String, String> map) {
        map.put("udid", getUDID(context));
    }

    public static void appendUserKey(Context context, Map<String, String> map) {
        String userKey = UserInfoUtil.getUserKey(context);
        if (TextUtils.isEmpty(userKey)) {
            return;
        }
        map.put("userkey", userKey);
    }

    public static synchronized String getUDID(Context context) {
        String encode3Des;
        synchronized (AHAPIHelper.class) {
            StringBuilder sb = new StringBuilder();
            sb.append(AHDeviceUtil.getDeviceId(context));
            sb.append("|");
            sb.append(System.nanoTime());
            sb.append("|");
            sb.append(UserInfoUtil.getUserDeviceId(context));
            encode3Des = SecurityUtil.encode3Des(context, sb.toString());
        }
        return encode3Des;
    }

    public static String toSign(Context context, Map<String, String> map) {
        if (map == null) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        sb.append(getSignKey(context));
        for (Map.Entry<String, String> entry : map.entrySet()) {
            sb.append(entry.getKey() + entry.getValue());
        }
        sb.append(getSignKey(context));
        return SecurityUtil.encodeMD5(sb.toString()).toUpperCase();
    }
}
