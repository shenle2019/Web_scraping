package com.shenjiahang.netapp.net;

import android.text.TextUtils;
import android.util.Log;

import com.shenjiahang.netapp.App;
import com.shenjiahang.netapp.util.AppPrefs;

import java.io.IOException;

import okhttp3.Interceptor;
import okhttp3.Request;
import okhttp3.Response;

/**
 * 统一下发签名头 + token 的应用拦截器。
 * <p>
 * 业务代码完全不写 header，OkHttp 每次真正发出请求前由这里补齐：
 * ctime / hsign / Authorization / X-Client。
 * 逆向定位点：okhttp3.OkHttpClient.Builder.addInterceptor
 */
public class SignInterceptor implements Interceptor {

    private static final String TAG = "NetApp";

    @Override
    public Response intercept(Chain chain) throws IOException {
        String ctime = Signer.nowSeconds();
        Request origin = chain.request();

        Request.Builder builder = origin.newBuilder()
                .header("ctime", ctime)
                .header("hsign", Signer.headerSign(ctime))
                .header("X-Client", "netapp/1.0 (okhttp)");

        // 登录成功后，后续请求自动带上 token，业务层无感
        String token = AppPrefs.getToken(App.ctx());
        if (!TextUtils.isEmpty(token)) {
            builder.header("Authorization", "Bearer " + token);
        }

        Request signed = builder.build();
        Log.i(TAG, "interceptor -> " + signed.method() + " " + signed.url()
                + " ctime=" + ctime + " hsign=" + Signer.headerSign(ctime));

        Response response = chain.proceed(signed);
        Log.i(TAG, "interceptor <- " + response.code() + " " + signed.url());
        return response;
    }
}
