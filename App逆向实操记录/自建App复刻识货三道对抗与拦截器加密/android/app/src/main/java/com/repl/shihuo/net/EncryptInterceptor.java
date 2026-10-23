package com.repl.shihuo.net;

import android.util.Log;

import com.repl.shihuo.util.Crypto;

import org.json.JSONObject;

import java.io.IOException;

import okhttp3.HttpUrl;
import okhttp3.Interceptor;
import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.ResponseBody;

/**
 * 复刻课件 6.4 节：拦截器里做请求加密与响应解密。
 *
 * 只处理老版本详情接口：
 *   goods_id=xxx  ->  data=Base64(AES({"goods_id":"xxx"}))
 *   服务端密文进密文出；拦截器再把响应解密回明文。
 *
 * 因此把本拦截器从链上摘掉（chain.proceed），请求就是明文，服务端也会回明文 —— 这就是课件的绕过点。
 */
public class EncryptInterceptor implements Interceptor {

    private static final String TAG = "EncryptInterceptor";
    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    @Override
    public Response intercept(Chain chain) throws IOException {
        Request request = chain.request();
        String path = request.url().encodedPath();
        if (!path.endsWith("/app_swoole_shoe/preload/single")) {
            return chain.proceed(request);
        }

        String goodsId = request.url().queryParameter("goods_id");
        if (goodsId == null) {
            return chain.proceed(request);
        }

        String plain = "{\"goods_id\":\"" + goodsId + "\"}";
        String encrypted;
        try {
            encrypted = Crypto.aesEncryptBase64(plain);
        } catch (Exception e) {
            throw new IOException("请求加密失败", e);
        }
        Log.i(TAG, "请求加密: " + plain + " -> data=" + encrypted);

        HttpUrl newUrl = request.url().newBuilder()
                .removeAllQueryParameters("goods_id")
                .addQueryParameter("data", encrypted)
                .build();
        Response response = chain.proceed(request.newBuilder().url(newUrl).build());

        String body = response.body() == null ? "" : response.body().string();
        String out = body;
        try {
            JSONObject json = new JSONObject(body);
            if (json.opt("data") instanceof String) {
                String decrypted = Crypto.aesDecryptBase64(json.getString("data"));
                Log.i(TAG, "响应解密: " + decrypted);
                out = decrypted;
            }
        } catch (Exception e) {
            Log.w(TAG, "响应不是可解密的密文结构，按明文处理: " + e.getMessage());
        }
        return response.newBuilder().body(ResponseBody.create(JSON, out)).build();
    }
}
