package com.example.bililike;

import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.TreeMap;

/**
 * 复刻 day17 的 H7 请求体：
 *   TreeMap 排序拼串 -> sha256(明文+盐) -> 明文&sign=xxx -> 整体 AES-CBC。
 */
public final class ClickReport {

    public static final String PATH = "/x/report/click/android2";
    public static final String CONTENT_TYPE = "application/json; charset=utf-8";

    public static final class Payload {
        public final String plain;
        public final String sign;
        public final byte[] body;

        Payload(String plain, String sign, byte[] body) {
            this.plain = plain;
            this.sign = sign;
            this.body = body;
        }
    }

    private ClickReport() {
    }

    public static Payload build(DeviceProfile p, long aid, long cid, int duration) {
        long now = System.currentTimeMillis();
        TreeMap<String, String> params = new TreeMap<>();
        params.put("aid", String.valueOf(aid));
        params.put("cid", String.valueOf(cid));
        params.put("part", "1");
        params.put("mid", "0");
        params.put("lv", "0");
        params.put("ftime", String.valueOf(now - 10000));
        params.put("stime", String.valueOf(now - 5000));
        params.put("did", p.deviceId);
        params.put("type", "3");
        params.put("sub_type", "0");
        params.put("sid", "0");
        params.put("epid", "0");
        params.put("auto_play", "0");
        params.put("build", "6240300");
        params.put("mobi_app", "android");
        params.put("spmid", "main.ugc-video-detail.0.0");
        params.put("from_spmid", "main.ugc-video-detail.0.0");
        params.put("video_duration", String.valueOf(duration));

        String plain = join(params);
        String sign = BiliCrypto.sha256Hex(
                plain.getBytes(StandardCharsets.UTF_8),
                BiliCrypto.SHA256_SALT.getBytes(StandardCharsets.UTF_8));
        byte[] body = BiliCrypto.aesEncrypt(plain + "&sign=" + sign);
        return new Payload(plain, sign, body);
    }

    public static String join(TreeMap<String, String> params) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : params.entrySet()) {
            if (sb.length() > 0) {
                sb.append('&');
            }
            sb.append(e.getKey()).append('=').append(e.getValue());
        }
        return sb.toString();
    }
}
