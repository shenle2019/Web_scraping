package com.repl.dewu;

import android.app.Activity;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Base64;
import android.widget.TextView;

import com.repl.dewu.net.Api;
import com.repl.dewu.net.NetClient;
import com.repl.dewu.update.UpdateChecker;
import com.repl.dewu.update.UpdateDialog;
import com.repl.dewu.util.SignUtils;

import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Random;

import okhttp3.HttpUrl;
import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MainActivity extends Activity {

    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    private TextView logView;
    private TextView statusView;
    private String uuid;
    private String token;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        logView = findViewById(R.id.tv_log);
        statusView = findViewById(R.id.tv_status);

        uuid = deviceUuid();
        refreshStatus();
        log("启动：uuid=" + uuid + "，v=" + Api.VERSION);

        UpdateChecker.check(this, latest -> runOnUiThread(() -> UpdateDialog.show(this, latest)));

        findViewById(R.id.btn_token).setOnClickListener(v -> new Thread(this::requestToken).start());
        findViewById(R.id.btn_feed).setOnClickListener(v -> new Thread(this::requestFeed).start());
        findViewById(R.id.btn_ping).setOnClickListener(v -> new Thread(this::pingBySystemProxy).start());
        findViewById(R.id.btn_clear).setOnClickListener(v -> logView.setText(""));
    }

    private void requestToken() {
        try {
            String ts = String.valueOf(System.currentTimeMillis());
            Map<String, String> params = baseParams(ts);

            log("---- 获取游客 Token ----");
            log("StringToSign: " + SignUtils.plain(params));
            String sign = SignUtils.newSign(params);
            log("newSign: " + sign);
            params.put("newSign", sign);

            JSONObject body = new JSONObject();
            for (Map.Entry<String, String> e : params.entrySet()) {
                body.put(e.getKey(), e.getValue());
            }

            Request request = new Request.Builder()
                    .url(Api.visitorToken())
                    .header("duuuid", uuid)
                    .header("duplatform", "android")
                    .header("appId", "duapp")
                    .header("duv", Api.VERSION)
                    .header("User-Agent", Api.UA)
                    .post(RequestBody.create(JSON, body.toString()))
                    .build();

            try (Response response = NetClient.API_CLIENT.newCall(request).execute()) {
                String text = response.body().string();
                token = response.header("X-Auth-Token");
                log("HTTP " + response.code() + " body=" + text);
                if (token != null) {
                    log("X-Auth-Token: " + token);
                    logJwtPayload(token);
                    refreshStatus();
                } else {
                    log("没有拿到 X-Auth-Token，检查 newSign 是否与参数一致");
                }
            }
        } catch (Exception e) {
            log("获取 Token 失败: " + e);
        }
    }

    private void requestFeed() {
        if (token == null) {
            log("请先获取 Token");
            return;
        }
        try {
            String ts = String.valueOf(System.currentTimeMillis());
            Map<String, String> params = new LinkedHashMap<>();
            params.put("lastId", "1");
            params.put("limit", "20");
            params.putAll(baseParams(ts));

            log("---- 拉取首页推荐流 ----");
            log("StringToSign: " + SignUtils.plain(params));
            String sign = SignUtils.newSign(params);
            log("newSign: " + sign);

            HttpUrl.Builder url = HttpUrl.parse(Api.feed()).newBuilder();
            for (Map.Entry<String, String> e : params.entrySet()) {
                url.addQueryParameter(e.getKey(), e.getValue());
            }
            url.addQueryParameter("newSign", sign);

            Request request = new Request.Builder()
                    .url(url.build())
                    .header("X-Auth-Token", token)
                    .header("User-Agent", Api.UA)
                    .build();

            try (Response response = NetClient.API_CLIENT.newCall(request).execute()) {
                String text = response.body().string();
                log("HTTP " + response.code() + " body=" + text);
            }
        } catch (Exception e) {
            log("拉取推荐流失败: " + e);
        }
    }

    private void pingBySystemProxy() {
        try {
            log("---- 代理对照 ping（PLAIN_CLIENT，走系统代理）----");
            Request request = new Request.Builder()
                    .url(Api.ping())
                    .header("User-Agent", Api.UA)
                    .build();
            try (Response response = NetClient.PLAIN_CLIENT.newCall(request).execute()) {
                log("HTTP " + response.code() + " body=" + response.body().string());
            }
        } catch (Exception e) {
            log("ping 失败: " + e);
        }
    }

    private Map<String, String> baseParams(String ts) {
        Map<String, String> params = new LinkedHashMap<>();
        params.put("loginToken", "");
        params.put("platform", "android");
        params.put("timestamp", ts);
        params.put("uuid", uuid);
        params.put("v", Api.VERSION);
        return params;
    }

    private String deviceUuid() {
        String id = Settings.Secure.getString(getContentResolver(), Settings.Secure.ANDROID_ID);
        if (id != null && id.length() >= 8) {
            return id.toLowerCase(Locale.US);
        }
        StringBuilder sb = new StringBuilder();
        Random random = new Random();
        for (int i = 0; i < 16; i++) {
            sb.append("0123456789abcdef".charAt(random.nextInt(16)));
        }
        return sb.toString();
    }

    private void logJwtPayload(String jwt) {
        try {
            String payload = jwt.split("\\.")[1];
            byte[] raw = Base64.decode(payload, Base64.URL_SAFE | Base64.NO_PADDING | Base64.NO_WRAP);
            log("JWT payload: " + new String(raw, StandardCharsets.UTF_8));
        } catch (Exception e) {
            log("JWT 解析失败: " + e);
        }
    }

    private void refreshStatus() {
        runOnUiThread(() -> statusView.setText(
                "uuid: " + uuid + "\n"
                        + "token: " + (token == null ? "-" : token.substring(0, Math.min(24, token.length())) + "..." )));
    }

    private void log(String message) {
        String time = new SimpleDateFormat("HH:mm:ss", Locale.US).format(new Date());
        runOnUiThread(() -> logView.append("[" + time + "] " + message + "\n"));
    }
}
