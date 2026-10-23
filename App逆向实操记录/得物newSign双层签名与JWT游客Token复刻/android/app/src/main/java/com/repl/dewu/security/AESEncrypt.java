package com.repl.dewu.security;

import java.nio.charset.StandardCharsets;

/**
 * 复刻课件里的 com.duapp.aesjni.AESEncrypt：
 * - getByteValues() 返回一串 0101（干扰项，so 内部并未使用）
 * - 逐位取反后传给 encodeByte
 * - encodeByte 在 so 里取固定 key，做 AES-128-ECB/PKCS5 + Base64
 */
public class AESEncrypt {

    static {
        System.loadLibrary("JNIEncrypt");
    }

    public static String encode(Object obj, String str) {
        String byteValues = getByteValues();
        StringBuilder sb = new StringBuilder(byteValues.length());
        for (int i = 0; i < byteValues.length(); i++) {
            sb.append(byteValues.charAt(i) == '0' ? '1' : '0');
        }
        return encodeByte(str.getBytes(StandardCharsets.UTF_8), sb.toString());
    }

    public static native String getByteValues();

    public static native String encodeByte(byte[] data, String mask);
}
