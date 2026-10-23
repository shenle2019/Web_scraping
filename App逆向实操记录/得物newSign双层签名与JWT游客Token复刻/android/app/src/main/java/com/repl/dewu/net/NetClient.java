package com.repl.dewu.net;

import java.net.Proxy;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;

public class NetClient {

    /** 业务请求：显式禁代理，复刻课件里"App 禁用手机端代理"的行为 */
    public static final OkHttpClient API_CLIENT = new OkHttpClient.Builder()
            .proxy(Proxy.NO_PROXY)
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build();

    /** 对照请求：不设置 proxy，跟随系统代理 */
    public static final OkHttpClient PLAIN_CLIENT = new OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build();

    private NetClient() {
    }
}
