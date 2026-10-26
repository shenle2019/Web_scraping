package com.example.bililike;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 复刻 com.bilibili.okretro.f.c 的 e(builder)：
 * 头里的 Buvid / Device-ID / fp_local / fp_remote / session_id 全部来自设备侧静态字段。
 */
public final class ReportInterceptor {

    private ReportInterceptor() {
    }

    public static Map<String, String> headers(DeviceProfile p) {
        Map<String, String> h = new LinkedHashMap<>();
        h.put("Display-ID", p.buvid + "-" + System.currentTimeMillis() + "-0");
        h.put("Buvid", p.buvid);
        h.put("User-Agent", "BiliDroid/6.24.0.0 os/android model/" + p.model
                + " mobi_app/android build/6240300 channel/master innerVer/6240300 osVer/11 network/2");
        h.put("Device-ID", p.deviceId);
        h.put("fp_local", p.fpLocal);
        h.put("fp_remote", p.fpRemote);
        h.put("session_id", p.sessionId);
        h.put("app-key", "android64");
        return h;
    }
}
