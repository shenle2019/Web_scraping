package com.shenjiahang.netapp.util;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * 与课件一致的 MD5 小工具：32 位小写、不足两位补 0。
 */
public final class Md5Utils {

    private Md5Utils() {
    }

    public static String md5(String text) {
        if (text == null) {
            text = "";
        }
        try {
            MessageDigest digest = MessageDigest.getInstance("MD5");
            byte[] bytes = digest.digest(text.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder(bytes.length * 2);
            for (byte b : bytes) {
                int value = b & 255;
                if (value < 16) {
                    sb.append('0');
                }
                sb.append(Integer.toHexString(value));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("当前环境不支持 MD5", e);
        }
    }
}
