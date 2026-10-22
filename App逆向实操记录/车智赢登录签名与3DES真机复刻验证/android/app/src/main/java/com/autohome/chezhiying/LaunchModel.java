package com.autohome.chezhiying;

import android.content.Context;
import android.util.Log;

import java.util.TreeMap;

/**
 * 复刻自车智赢的 LaunchModel.initRequestCommonParams：
 * 补齐公共参数 -> 生成 udid -> 对除 _sign 之外的字段签名 -> 写入 _sign。
 */
public class LaunchModel {

    private static final String TAG = "CheZhiYing";

    public static final String APP_ID = "atc.android";
    public static final String APP_VERSION = "3.56.0";
    public static final String CHANNEL_ID = "csy";

    public void initRequestCommonParams(int signType, TreeMap<String, String> params, Context context) {
        if (!params.containsKey("_appid")) {
            params.put("_appid", APP_ID);
        }
        if (!params.containsKey("channelid")) {
            params.put("channelid", CHANNEL_ID);
        }
        if (!params.containsKey("appversion")) {
            params.put("appversion", APP_VERSION);
        }
        if (!params.containsKey("udid")) {
            params.put("udid", AppUtils.getUDID(context));
        }
        checkNullParams(params);
        params.put("_sign", SignManager.INSTANCE.signByType(signType, params));
        Log.i(TAG, "request params=" + params);
    }

    private void checkNullParams(TreeMap<String, String> params) {
        for (String key : params.keySet()) {
            if (params.get(key) == null) {
                params.put(key, "");
            }
        }
    }
}
