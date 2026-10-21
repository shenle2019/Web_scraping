package com.shenjiahang.netapp.net;

/**
 * 全局网络配置。
 * BASE_URL 必须指向运行 Flask 靶场的电脑（手机与电脑同一局域网）。
 */
public final class NetConfig {

    /** 本地靶场地址，改这里即可换服务器 */
    public static final String BASE_URL = "http://192.168.31.220:8080/";

    /** 请求头签名盐值，与后端保持一致 */
    public static final String SALT = "SJH_2026_APP";

    /** SharedPreferences 文件名，落盘路径 /data/data/<包名>/shared_prefs/sp_token.xml */
    public static final String SP_NAME = "sp_token";
    public static final String SP_KEY_TOKEN = "token";
    public static final String SP_KEY_USER = "user";

    private NetConfig() {
    }
}
