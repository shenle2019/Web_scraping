package com.repl.shihuo.net;

import java.io.IOException;
import java.net.Proxy;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/**
 * 复刻课件 5.1 节的代理检测：
 * 业务客户端显式 proxy(Proxy.NO_PROXY)，完全无视系统代理，Charles 抓不到；
 * 另留一个 PLAIN_CLIENT 走系统代理，作为对照。
 */
public final class NetClient {

    private static final OkHttpClient API_CLIENT = new OkHttpClient.Builder()
            .proxy(Proxy.NO_PROXY)
            .addInterceptor(new EncryptInterceptor())
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .build();

    private static final OkHttpClient PLAIN_CLIENT = new OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .build();

    private NetClient() {
    }

    public static OkHttpClient api() {
        return API_CLIENT;
    }

    public static OkHttpClient plain() {
        return PLAIN_CLIENT;
    }

    public static String execute(OkHttpClient client, Request request) throws IOException {
        try (Response response = client.newCall(request).execute()) {
            return response.body() == null ? "" : response.body().string();
        }
    }
}
