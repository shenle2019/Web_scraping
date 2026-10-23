package com.repl.dewu.util;

import com.repl.dewu.security.AESEncrypt;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Map;
import java.util.TreeMap;

public class SignUtils {

    /** 排序后直接拼 key+value，没有分隔符 */
    public static String plain(Map<String, String> params) {
        TreeMap<String, String> sorted = new TreeMap<>(params);
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : sorted.entrySet()) {
            sb.append(e.getKey()).append(e.getValue());
        }
        return sb.toString();
    }

    /** newSign = md5( base64( aes_ecb(plain) ) ) */
    public static String newSign(Map<String, String> params) {
        String encoded = AESEncrypt.encode(null, plain(params));
        return md5(encoded);
    }

    public static String md5(String text) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(text.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                String hex = Integer.toHexString(b & 0xFF);
                if (hex.length() < 2) {
                    sb.append('0');
                }
                sb.append(hex);
            }
            return sb.toString();
        } catch (Exception e) {
            return "";
        }
    }
}
