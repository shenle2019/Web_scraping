package com.shenjiahang.netapp.net;

import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;

/**
 * 全局唯一的 OkHttpClient：OkHttp 官方建议复用连接池与线程池。
 * Retrofit 也复用同一个 client，保证拦截器对两条链路都生效。
 */
public final class Http {

    private static volatile OkHttpClient client;

    private Http() {
    }

    public static OkHttpClient get() {
        if (client == null) {
            synchronized (Http.class) {
                if (client == null) {
                    client = new OkHttpClient.Builder()
                            .connectTimeout(8, TimeUnit.SECONDS)
                            .readTimeout(8, TimeUnit.SECONDS)
                            .addInterceptor(new SignInterceptor())
                            .build();
                }
            }
        }
        return client;
    }
}
