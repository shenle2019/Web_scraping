package com.repl.dewu.update;

import android.content.Context;

import com.repl.dewu.net.Api;
import com.repl.dewu.net.NetClient;

import org.json.JSONObject;

import okhttp3.Request;
import okhttp3.Response;

public class UpdateChecker {

    public interface Callback {
        void onResult(String latest);
    }

    public static void check(Context context, Callback callback) {
        new Thread(() -> {
            try {
                Request request = new Request.Builder()
                        .url(Api.version())
                        .header("User-Agent", Api.UA)
                        .build();
                try (Response response = NetClient.PLAIN_CLIENT.newCall(request).execute()) {
                    JSONObject root = new JSONObject(response.body().string());
                    JSONObject data = root.optJSONObject("data");
                    if (data != null && data.optBoolean("force")) {
                        callback.onResult(data.optString("latest"));
                    }
                }
            } catch (Exception ignored) {
                // 断网时静默失败，模拟课件里的"断网启动绕过更新"
            }
        }).start();
    }
}
