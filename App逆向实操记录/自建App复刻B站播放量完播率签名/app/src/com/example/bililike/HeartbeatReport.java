package com.example.bililike;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Random;
import java.util.TreeMap;

/**
 * 复刻 day19 的完播率请求：
 *   session = sha1(buvid + 毫秒时间戳 + rand(0,1e6))，无盐；
 *   sign    = so 层 md5(排序明文 + 四段盐)，明文与 sign 以表单体发送。
 */
public final class HeartbeatReport {

    public static final String PATH = "/x/report/heartbeat/mobile";
    public static final String CONTENT_TYPE = "application/x-www-form-urlencoded; charset=utf-8";

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

    private HeartbeatReport() {
    }

    /** 对应 g.a.a()：buvid 取不到时为空串，这里保留 buvid 以贴合真机形态 */
    public static String newSession(DeviceProfile p) {
        String raw = p.buvid + System.currentTimeMillis() + new Random().nextInt(1000000);
        return BiliCrypto.sha1Hex(raw);
    }

    public static Payload build(DeviceProfile p, long aid, long cid, int duration,
                                long startTs, boolean end, String session) {
        long now = System.currentTimeMillis();
        long total = (now - startTs) / 1000L;
        long played = end ? duration : 0;
        long paused = end ? Math.max(0, total - duration) : 0;

        TreeMap<String, String> params = new TreeMap<>();
        params.put("aid", String.valueOf(aid));
        params.put("cid", String.valueOf(cid));
        params.put("sid", "0");
        params.put("epid", "0");
        params.put("type", "3");
        params.put("sub_type", "0");
        params.put("quality", "32");
        params.put("video_duration", String.valueOf(duration));
        params.put("played_time", String.valueOf(played));
        params.put("paused_time", String.valueOf(paused));
        params.put("total_time", String.valueOf(end ? total : 0));
        params.put("actual_played_time", String.valueOf(played));
        params.put("last_play_progress_time", String.valueOf(played));
        params.put("max_play_progress_time", String.valueOf(played));
        params.put("start_ts", String.valueOf(startTs / 1000L));
        params.put("ts", String.valueOf(now / 1000L));
        params.put("statistics", "{\"autoplay\":1,\"card_type\":0,\"platform\":\"android\"}");
        params.put("session", session);

        TreeMap<String, String> encoded = new TreeMap<>();
        for (Map.Entry<String, String> e : params.entrySet()) {
            encoded.put(e.getKey(), urlEncode(e.getValue()));
        }
        String plain = ClickReport.join(encoded);
        String sign = BiliSign.nativeSign(plain);
        return new Payload(plain, sign, (plain + "&sign=" + sign).getBytes(StandardCharsets.UTF_8));
    }

    private static String urlEncode(String v) {
        try {
            return URLEncoder.encode(v, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }
    }
}
