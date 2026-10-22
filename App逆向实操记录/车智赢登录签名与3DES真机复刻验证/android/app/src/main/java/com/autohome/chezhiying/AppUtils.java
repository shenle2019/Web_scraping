package com.autohome.chezhiying;

import android.content.Context;
import android.provider.Settings;
import android.telephony.TelephonyManager;
import android.text.TextUtils;
import android.util.Log;

import com.autohome.ahkit.utils.SecurityUtil;

import java.net.NetworkInterface;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

/**
 * 复刻自车智赢的 AppUtils.getUDID：
 * 明文 = imei | System.nanoTime() | deviceId，整体过 3DES 后 Base64。
 */
public class AppUtils {

    private static final String TAG = "CheZhiYing";
    private static final String SEPARATOR = "|";

    public static String getUDID(Context context) {
        String imei = getIMEI(context);
        long nanoTime = System.nanoTime();
        String deviceId = SPUtils.getDeviceId(context);
        String plain = imei + SEPARATOR + nanoTime + SEPARATOR + deviceId;
        String udid = SecurityUtil.encode3Des(context, plain);
        Log.i(TAG, "udid plain=" + plain);
        Log.i(TAG, "udid cipher=" + udid);
        return udid;
    }

    /** 四级降级，与真实实现一致：SP 缓存 -> 真 IMEI -> MAC 转 UUID -> AndroidID 转 UUID -> 兜底 sssss */
    public static String getIMEI(Context context) {
        String imei = SPUtils.getIMEI(context);
        if (!TextUtils.isEmpty(imei)) {
            return imei;
        }
        try {
            TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
            if (tm != null) {
                imei = tm.getDeviceId();
            }
        } catch (Exception ignored) {
        }
        if (TextUtils.isEmpty(imei)) {
            imei = getIMEIbyMac();
        }
        if (TextUtils.isEmpty(imei)) {
            imei = getIMEIbyAndroidIDandUUID(context);
        }
        if (TextUtils.isEmpty(imei)) {
            imei = "sssss";
        }
        SPUtils.saveIMEI(context, imei);
        Log.i(TAG, "getIMEI -> " + imei);
        return imei;
    }

    private static String getIMEIbyMac() {
        try {
            List<NetworkInterface> all = Collections.list(NetworkInterface.getNetworkInterfaces());
            for (NetworkInterface ni : all) {
                if (ni.getName().equalsIgnoreCase("wlan0")) {
                    byte[] mac = ni.getHardwareAddress();
                    if (mac != null) {
                        return UUID.nameUUIDFromBytes(mac).toString();
                    }
                }
            }
        } catch (Exception ignored) {
        }
        return "";
    }

    private static String getIMEIbyAndroidIDandUUID(Context context) {
        String androidId = Settings.Secure.getString(context.getContentResolver(), Settings.Secure.ANDROID_ID);
        if (TextUtils.isEmpty(androidId)) {
            return "";
        }
        return UUID.nameUUIDFromBytes(androidId.getBytes()).toString();
    }
}
