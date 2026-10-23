package com.repl.shihuo.update;

import android.os.Handler;
import android.os.Looper;

import com.repl.shihuo.BuildConfig;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * 启动时请求 /app/version 比对版本号，服务端说强制更新就弹不可取消的窗。
 * 对应课件"App 一启动就请求最新版本号，与本地比对"的逻辑。
 */
public final class UpdateChecker {

    public interface Callback {
        void onResult(boolean force, String latest);
    }

    private UpdateChecker() {
    }

    public static void check(Callback callback) {
        new Thread(() -> {
            boolean force = false;
            String latest = BuildConfig.VERSION_NAME;
            try {
                HttpURLConnection conn = (HttpURLConnection) new URL(
                        BuildConfig.BASE_URL + "/app/version").openConnection();
                conn.setConnectTimeout(5000);
                conn.setReadTimeout(5000);
                StringBuilder sb = new StringBuilder();
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(conn.getInputStream(), "UTF-8"))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        sb.append(line);
                    }
                }
                JSONObject data = new JSONObject(sb.toString()).getJSONObject("data");
                latest = data.optString("latest", latest);
                force = data.optBoolean("force", false) && !latest.equals(BuildConfig.VERSION_NAME);
            } catch (Exception ignored) {
                // 服务端未启动时静默降级，方便离线验证
            }
            final boolean resultForce = force;
            final String resultLatest = latest;
            new Handler(Looper.getMainLooper()).post(() -> callback.onResult(resultForce, resultLatest));
        }).start();
    }
}
