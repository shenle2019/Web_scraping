package com.repl.shihuo.net;

import com.repl.shihuo.BuildConfig;

import org.json.JSONObject;

import okhttp3.HttpUrl;
import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;

/**
 * 按课件抓包结果复刻的四个接口调用。
 * 老接口免头明文、新接口带风控头、老详情交给拦截器加密、新详情免头明文。
 */
public final class Api {

    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    // 课件里老版本搜索只靠这一个 UA，其余请求头都能删；sh-dv-sign 写死即可
    private static final String UA_OLD = "Android 11 {Z29vZ2xl} CPU_ABI arm64-v8a CPU_ABI2  "
            + "HARDWARE taimen MODEL {UGl4ZWwgMiBYTA} network/WIFI shihuo/7.20.1 "
            + "sc({holder},myapp) minVersion(15670) sh-dv-sign[v1|repl]";

    private Api() {
    }

    public static String searchOld(String keyword) throws Exception {
        JSONObject body = new JSONObject();
        body.put("keywords", keyword);
        body.put("page", "1");
        body.put("pageSize", "20");

        HttpUrl url = HttpUrl.parse(BuildConfig.BASE_URL + "/daga/search/goods/v1").newBuilder()
                .addQueryParameter("minVersion", "15670")
                .addQueryParameter("clientCode", "{holder}")
                .addQueryParameter("v", "7.20.1")
                .addQueryParameter("channel", "myapp")
                .addQueryParameter("device", "Pixel 2 XL")
                .addQueryParameter("platform", "android")
                .addQueryParameter("timestamp", String.valueOf(System.currentTimeMillis()))
                .build();

        Request request = new Request.Builder()
                .url(url)
                .header("user-agent", UA_OLD)
                .post(RequestBody.create(JSON, body.toString()))
                .build();
        return NetClient.execute(NetClient.api(), request);
    }

    public static String searchNew(String keyword) throws Exception {
        JSONObject body = new JSONObject();
        body.put("keywords", keyword);
        body.put("page", "1");
        body.put("pageSize", "20");

        HttpUrl url = HttpUrl.parse(BuildConfig.BASE_URL + "/v3/sh-api/daga/search/goods/v1").newBuilder()
                .addQueryParameter("minVersion", "19612")
                .addQueryParameter("clientCode", "%7Bholder%7D")
                .addQueryParameter("v", "7.73.0")
                .addQueryParameter("channel", "ali")
                .addQueryParameter("device", "Pixel%202%20XL")
                .addQueryParameter("platform", "android")
                .addQueryParameter("timestamp", String.valueOf(System.currentTimeMillis()))
                .build();

        Request request = new Request.Builder()
                .url(url)
                .header("user-agent", UA_OLD)
                .header("sh-sign", "F6D9FB867DE1F7542200743BF8B1BA2A")
                .header("sh-token", "REPL-TOKEN-7.20.1")
                .header("app-v", "7.20.1")
                .header("platform", "android")
                .header("osv", "11")
                .header("network", "1")
                .post(RequestBody.create(JSON, body.toString()))
                .build();
        return NetClient.execute(NetClient.api(), request);
    }

    public static String detailOld(String goodsId) throws Exception {
        HttpUrl url = HttpUrl.parse(BuildConfig.BASE_URL
                        + "/v4/services/sh-goodsapi/app_swoole_shoe/preload/single").newBuilder()
                .addQueryParameter("goods_id", goodsId)
                .addQueryParameter("v", "7.20.1")
                .build();
        Request request = new Request.Builder()
                .url(url)
                .header("app-v", "7.20.1")
                .header("platform", "android")
                .get()
                .build();
        return NetClient.execute(NetClient.api(), request);
    }

    public static String detailNew(String goodsId) throws Exception {
        HttpUrl url = HttpUrl.parse(BuildConfig.BASE_URL
                        + "/v4/services/sh-goodsapi/public/detail").newBuilder()
                .addQueryParameter("goods_id", goodsId)
                .addQueryParameter("v", "7.73.0")
                .build();
        Request request = new Request.Builder().url(url).get().build();
        return NetClient.execute(NetClient.api(), request);
    }

    public static String contrast() throws Exception {
        Request request = new Request.Builder()
                .url(BuildConfig.BASE_URL + "/app/ping")
                .get()
                .build();
        return NetClient.execute(NetClient.plain(), request);
    }
}
