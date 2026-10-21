package com.shenjiahang.netapp.api;

import com.shenjiahang.netapp.net.Http;
import com.shenjiahang.netapp.net.NetConfig;

import retrofit2.Retrofit;

/**
 * 故意不显式 .client(Http.get()) 就会用 Retrofit 自己新建的 client，
 * 拦截器不生效 —— 这是课件里强调的坑，这里显式绑定。
 */
public final class ApiFactory {

    private static volatile ApiService service;

    private ApiFactory() {
    }

    public static ApiService get() {
        if (service == null) {
            synchronized (ApiFactory.class) {
                if (service == null) {
                    Retrofit retrofit = new Retrofit.Builder()
                            .baseUrl(NetConfig.BASE_URL)
                            .client(Http.get())
                            .build();
                    service = retrofit.create(ApiService.class);
                }
            }
        }
        return service;
    }
}
