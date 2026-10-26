package com.achievo.vipshop.repl;

import android.app.Activity;
import android.os.Bundle;
import android.util.Base64;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Map;
import java.util.Random;
import java.util.TreeMap;
import java.util.UUID;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * 仅限学习研究，禁止商用。
 * 唯品会 v7.83.3 搜索功能四接口签名链复刻 App
 * 复刻课件：day20-唯品会01、day21-唯品会02
 * 接口链：device_reg -> getTokenByFP -> generate_token -> 搜索
 */
public class MainActivity extends Activity {

    // ---------- 破解出的固定值（与课件 hook 输出一致） ----------
    private static final String API_KEY = "23e7f28019e8407b98b84cd05b5aef2c";
    private static final String SKEY = "6692c461c3810ab150c9a980d0c275ec";
    private static final String VCSP_KEY = "4d9e524ad536c03ff203787cf0dfcd29";
    private static final String SALT = "aee4c425dbb2288b80c71347cc37d04b";       // api_sign 盐 / AES key 原料
    private static final String VCSP_SIGN = "05a68135d2bfd322e3a22f95bbc25a24c777f387";
    private static final String CHANNEL = "oziq7dxw:::";

    private TextView mLog;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        final EditText input = new EditText(this);
        input.setHint("输入商品关键字，如 外套女");
        input.setText("nike");  // 预填默认关键字，方便一键验证
        Button btn = new Button(this);
        btn.setText("执行四接口签名链搜索");
        mLog = new TextView(this);
        mLog.setTextIsSelectable(true);
        ScrollView scroll = new ScrollView(this);
        scroll.addView(mLog);

        android.widget.LinearLayout root = new android.widget.LinearLayout(this);
        root.setOrientation(android.widget.LinearLayout.VERTICAL);
        root.setPadding(24, 24, 24, 24);
        root.addView(input);
        root.addView(btn);
        root.addView(scroll);
        setContentView(root);

        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                final String keyword = input.getText().toString().trim();
                if (keyword.isEmpty()) {
                    log("请先输入关键字");
                    return;
                }
                mLog.setText("");
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            runChain(keyword);
                        } catch (Exception e) {
                            log("异常: " + e);
                            for (StackTraceElement s : e.getStackTrace()) {
                                log("    at " + s.toString());
                            }
                        }
                    }
                }).start();
            }
        });
    }

    private void log(final String s) {
        android.util.Log.d("VipRepl", s);
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                mLog.append(s + "\n");
            }
        });
    }

    // ---------- 算法实现（与课件破解结论一致） ----------

    private static String sha1Hex(String s) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-1");
        byte[] d = md.digest(s.getBytes(StandardCharsets.UTF_8));
        StringBuilder sb = new StringBuilder();
        for (byte b : d) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    /** api_sign = sha1(SALT + sha1(SALT + 排序后参数串))，双层 sha1 */
    private static String apiSign(String ordered) throws Exception {
        String tmp = sha1Hex(SALT + ordered);
        return sha1Hex(SALT + tmp);
    }

    private static String sortedQuery(TreeMap<String, String> params) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : params.entrySet()) {
            if (sb.length() > 0) {
                sb.append("&");
            }
            sb.append(e.getKey()).append("=").append(e.getValue());
        }
        return sb.toString();
    }

    /** AES key = md5(SALT) 的 16 字节 digest */
    private static byte[] aesKey() throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        return md.digest(SALT.getBytes(StandardCharsets.UTF_8));
    }

    /** iv = 16 位随机 hex（1~f） */
    private static String randHex16() {
        StringBuilder sb = new StringBuilder();
        Random r = new Random();
        for (int i = 0; i < 16; i++) {
            sb.append(Integer.toHexString(r.nextInt(15) + 1));
        }
        return sb.toString();
    }

    /** edata = base64(iv_bytes + AES_CBC_PKCS5(明文)) */
    private static String makeEdata(String plain, byte[] key) throws Exception {
        String iv = randHex16();
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE,
                new SecretKeySpec(key, "AES"),
                new IvParameterSpec(iv.getBytes(StandardCharsets.UTF_8)));
        byte[] enc = cipher.doFinal(plain.getBytes(StandardCharsets.UTF_8));
        byte[] out = new byte[iv.length() + enc.length];
        System.arraycopy(iv.getBytes(StandardCharsets.UTF_8), 0, out, 0, iv.length());
        System.arraycopy(enc, 0, out, iv.length(), enc.length);
        return Base64.encodeToString(out, Base64.NO_WRAP);
    }

    /** Python quote_plus 等价：URLEncoder 再把 '+' 换成 '%20' */
    private static String quotePlus(String s) throws Exception {
        return URLEncoder.encode(s, "UTF-8").replace("+", "%20");
    }

    private static String httpGet(String url, Map<String, String> headers) throws Exception {
        HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
        conn.setConnectTimeout(20000);
        conn.setReadTimeout(20000);
        if (headers != null) {
            for (Map.Entry<String, String> e : headers.entrySet()) {
                conn.setRequestProperty(e.getKey(), e.getValue());
            }
        }
        int code = conn.getResponseCode();
        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            sb.append(line);
        }
        br.close();
        conn.disconnect();
        return "HTTP " + code + " " + sb;
    }

    private static String httpPost(String url, TreeMap<String, String> form, Map<String, String> headers) throws Exception {
        StringBuilder body = new StringBuilder();
        for (Map.Entry<String, String> e : form.entrySet()) {
            if (body.length() > 0) {
                body.append("&");
            }
            body.append(URLEncoder.encode(e.getKey(), "UTF-8"))
                    .append("=")
                    .append(URLEncoder.encode(e.getValue(), "UTF-8"));
        }
        HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
        conn.setRequestMethod("POST");
        conn.setConnectTimeout(20000);
        conn.setReadTimeout(20000);
        conn.setDoOutput(true);
        conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        if (headers != null) {
            for (Map.Entry<String, String> e : headers.entrySet()) {
                conn.setRequestProperty(e.getKey(), e.getValue());
            }
        }
        OutputStream os = conn.getOutputStream();
        os.write(body.toString().getBytes(StandardCharsets.UTF_8));
        os.flush();
        os.close();
        int code = conn.getResponseCode();
        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            sb.append(line);
        }
        br.close();
        conn.disconnect();
        return "HTTP " + code + " " + sb;
    }

    private static Map<String, String> headersOf(String... kv) {
        Map<String, String> m = new java.util.HashMap<String, String>();
        for (int i = 0; i + 1 < kv.length; i += 2) {
            m.put(kv[i], kv[i + 1]);
        }
        return m;
    }

    // ---------- 四接口签名链 ----------

    private void runChain(String keyword) throws Exception {
        String marsCid = UUID.randomUUID().toString();
        String deviceToken = UUID.randomUUID().toString();
        String androidId = randHex16();
        String buildModel = "Pixel 2 XL";
        String ctime = String.valueOf(System.currentTimeMillis() / 1000);
        byte[] key = aesKey();

        // ===== 1. device_reg 注册设备 =====
        TreeMap<String, String> p1 = new TreeMap<String, String>();
        p1.put("app_name", "achievo_ad");
        p1.put("app_version", "7.83.3");
        p1.put("device_token", deviceToken);
        p1.put("status", "1");
        p1.put("warehouse", "null");
        p1.put("manufacturer", "Google");
        p1.put("device", buildModel);
        p1.put("os_version", "30");
        p1.put("channel", CHANNEL);
        p1.put("vipruid", "");
        p1.put("regPlat", "0");
        p1.put("regid", "");
        p1.put("rom", "Dalvik/2.1.0 (Linux; U; Android 11; Pixel 2 XL Build/RP1A.201005.004.A1)");
        p1.put("skey", SKEY);
        String q1 = sortedQuery(p1);
        log("========== [1] device_reg ==========");
        log("ordered: " + q1.substring(0, 80) + "...");
        log("api_sign: " + apiSign(q1));
        String url1 = "https://mp.appvipshop.com/apns/device_reg?" + buildForm(p1);
        log("resp: " + httpGet(url1, headersOf("Authorization", "OAuth api_sign=" + apiSign(q1))));
        Thread.sleep(1000);

        // ===== 2. getTokenByFP 拿 vcspToken =====
        log("========== [2] getTokenByFP ==========");
        String r2 = httpGet("https://vcsp-api.vip.com/token/getTokenByFP?vcspKey=" + VCSP_KEY,
                headersOf("vcspauthorization", "vcspSign=" + VCSP_SIGN));
        log("resp: " + r2.substring(0, Math.min(200, r2.length())));
        String vcspToken = new JSONObject(r2.substring(r2.indexOf('{'))).getJSONObject("data").getString("vcspToken");
        log("vcspToken: " + vcspToken);
        Thread.sleep(1000);

        // ===== 3. generate_token 拿 did =====
        log("========== [3] generate_token ==========");
        String dinfo = "{\"ah1\":\"\",\"ah2\":\"\",\"ah3\":\"\",\"ah4\":\"wifi\",\"ah5\":\"1440_2712\",\"ah6\":1900800,"
                + "\"ah7\":8,\"ah8\":3839954944,\"ah9\":\"" + buildModel + "\",\"ah10\":\"\",\"ah11\":\"\",\"ah12\":\"\",\"ah13\":\"\","
                + "\"as1\":\"11\",\"as2\":\"\",\"as3\":\"\",\"as4\":\"" + androidId + "\",\"as5\":\"\",\"as6\":\"\",\"as7\":\"30\","
                + "\"ac1\":\"" + deviceToken + "\"}";
        TreeMap<String, String> p3 = new TreeMap<String, String>();
        p3.put("app_name", "shop_android");
        p3.put("app_version", "7.83.3");
        p3.put("client_type", "android");
        p3.put("dinfo", quotePlus(dinfo));
        p3.put("mars_cid", marsCid);
        p3.put("phone_model", buildModel);
        p3.put("session_id", marsCid + "_shop_android_" + ctime);
        p3.put("sys_version", "30");
        p3.put("vcspKey", VCSP_KEY);
        p3.put("vcspToken", vcspToken);
        String edata = makeEdata(sortedQuery(p3), key);
        log("edata 前 40: " + edata.substring(0, 40));
        TreeMap<String, String> body3 = new TreeMap<String, String>();
        body3.put("api_key", API_KEY);
        body3.put("did", "");
        body3.put("edata", edata);
        body3.put("eversion", "0");
        body3.put("skey", SKEY);
        body3.put("timestamp", String.valueOf(System.currentTimeMillis() / 1000));
        String r3 = httpPost("https://mapi.appvipshop.com/vips-mobile/rest/device/generate_token",
                body3, headersOf("Authorization", "OAuth api_sign=" + apiSign(sortedQuery(body3))));
        log("resp: " + r3.substring(0, Math.min(300, r3.length())));
        String did = new JSONObject(r3.substring(r3.indexOf('{'))).getJSONObject("data").getJSONObject("token").getString("did");
        log("did: " + did);
        Thread.sleep(1000);

        // ===== 4. 搜索 =====
        log("========== [4] 搜索 keyword=" + keyword + " ==========");
        long nowMs = System.currentTimeMillis();
        TreeMap<String, String> s = new TreeMap<String, String>();
        s.put("api_key", API_KEY);
        s.put("app_name", "shop_android");
        s.put("app_version", "7.83.3");
        s.put("bigSaleTagIds", "");
        s.put("brandIds", "");
        s.put("brandStoreSns", "");
        s.put("categoryId", "");
        s.put("channelId", "1");
        s.put("channel_flag", "0_1");
        s.put("client", "android");
        s.put("client_type", "android");
        s.put("darkmode", "0");
        s.put("deeplink_cps", "");
        s.put("device_model", buildModel);
        s.put("did", did);
        s.put("elder", "0");
        s.put("extParams", "{\"priceVer\":\"2\",\"mclabel\":\"1\",\"cmpStyle\":\"1\",\"statusVer\":\"2\","
                + "\"ic2label\":\"1\",\"video\":\"2\",\"uiVer\":\"2\",\"preheatTipsVer\":\"4\","
                + "\"floatwin\":\"1\",\"superHot\":\"1\",\"exclusivePrice\":\"1\",\"router\":\"1\","
                + "\"coupons\":\"1\",\"needVideoExplain\":\"1\",\"rank\":\"2\",\"needVideoGive\":\"1\","
                + "\"bigBrand\":\"1\",\"couponVer\":\"v2\",\"videoExplainUrl\":\"1\",\"live\":\"1\","
                + "\"sellpoint\":\"1\",\"reco\":\"1\",\"vreimg\":\"1\",\"search_tag\":\"2\",\"tpl\":\"1\","
                + "\"stdSizeVids\":\"\",\"labelVer\":\"2\"}");
        s.put("fdc_area_id", "103101101109");
        s.put("functions", "RTRecomm,flagshipInfo,feedback,otdAds,zoneCode,slotOp,survey,hasTabs,floaterParams");
        s.put("harmony_app", "0");
        s.put("harmony_os", "0");
        s.put("headTabType", "all");
        s.put("height", "2712");
        s.put("isMultiTab", "0");
        s.put("keyword", keyword);
        s.put("lastPageProperty", "{\"isBgToFront\":\"0\",\"suggest_text\":\"" + keyword + "\",\"scene_entry_id\":\"-99\","
                + "\"refer_page_id\":\"page_te_globle_classify_search_" + (nowMs - 200) + "\",\"text\":\"" + keyword + "\",\"tag\":\"1\","
                + "\"module_name\":\"com.achievo.vipshop.search\",\"type\":\"all\",\"typename\":\"全部\","
                + "\"is_back_page\":\"0\"}");
        s.put("maker", "GOOGLE");
        s.put("mars_cid", marsCid);
        s.put("mobile_channel", CHANNEL);
        s.put("mobile_platform", "3");
        s.put("net", "WIFI");
        s.put("operator", "");
        s.put("os", "Android");
        s.put("osv", "11");
        s.put("otddid", "");
        s.put("other_cps", "");
        s.put("page_id", "page_te_commodity_search_" + nowMs);
        s.put("phone_model", buildModel.toLowerCase());
        s.put("priceMax", "");
        s.put("priceMin", "");
        s.put("props", "");
        s.put("province_id", "103101");
        s.put("referer", "com.achievo.vipshop.search.activity.TabSearchProductListActivity");
        s.put("rom", "Dalvik/2.1.0 (Linux; U; Android 11; Pixel 2 XL Build/RP1A.201005.004.A1)");
        s.put("sd_tuijian", "0");
        s.put("service_provider", "");
        s.put("session_id", marsCid + "_shop_android_" + ctime);
        s.put("skey", SKEY);
        s.put("sort", "0");
        s.put("source", "app");
        s.put("source_app", "android");
        s.put("standby_id", CHANNEL);
        s.put("sys_version", "30");
        s.put("timestamp", ctime);
        s.put("union_mark", "blank&_&blank&_&oziq7dxw:::&_&blank&_&blank");
        s.put("vipService", "");
        s.put("warehouse", "VIP_SH");
        s.put("width", "1440");

        String q4 = sortedQuery(s);
        log("api_sign: " + apiSign(q4));
        String r4 = httpPost("https://mapi.appvipshop.com/vips-mobile/rest/shopping/search/product/list/v1",
                s, headersOf("Authorization", "OAuth api_sign=" + apiSign(q4)));
        log("resp: " + r4.substring(0, Math.min(300, r4.length())));
        try {
            JSONObject j = new JSONObject(r4.substring(r4.indexOf('{')));
            org.json.JSONArray products = j.optJSONArray("products");
            if (products == null) {
                log("响应无 products 字段（可能被风控拦截，如 code=11000 Forbidden by TFS）");
            } else {
                log("商品数: " + products.length());
                for (int i = 0; i < Math.min(10, products.length()); i++) {
                    JSONObject p = products.getJSONObject(i);
                    String title = p.optString("productName", "");
                    if (title.isEmpty()) {
                        title = p.optString("title", "");
                    }
                    log("  - " + title);
                }
            }
        } catch (Exception e) {
            log("响应解析失败: " + e.getMessage());
        }
        log("========== 接口链执行结束 ==========");
    }

    /** TreeMap 已排序，转成 k=v&k=v 的 URL query（不编码值，与签名原文一致） */
    private static String buildForm(TreeMap<String, String> params) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : params.entrySet()) {
            if (sb.length() > 0) {
                sb.append("&");
            }
            sb.append(URLEncoder.encode(e.getKey())).append("=").append(URLEncoder.encode(e.getValue()));
        }
        return sb.toString();
    }
}
