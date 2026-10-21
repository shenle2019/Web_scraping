package com.shenjiahang.netapp.api;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Field;
import retrofit2.http.FormUrlEncoded;
import retrofit2.http.GET;
import retrofit2.http.POST;

/**
 * Retrofit 注解式接口：方法体不用写，路径拼接在 baseUrl 后面。
 * 返回 ResponseBody 是为了演示"Retrofit 只负责发请求，解析仍旧交给 Gson"，
 * 也避免额外引入 converter-gson 依赖。
 */
public interface ApiService {

    @FormUrlEncoded
    @POST("login")
    Call<ResponseBody> login(@Field("user") String user,
                             @Field("pwd") String pwd,
                             @Field("sign") String sign,
                             @Field("t1") String t1);

    @GET("films")
    Call<ResponseBody> films();
}
