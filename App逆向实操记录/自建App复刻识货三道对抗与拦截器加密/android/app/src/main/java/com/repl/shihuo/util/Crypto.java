package com.repl.shihuo.util;

import android.util.Base64;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

/**
 * 与本地服务端 server/app.py 对应的 AES/ECB/PKCS5Padding + Base64。
 * 课件里算法藏在 so 中，这里等价地写死在客户端，便于观察拦截器行为。
 */
public final class Crypto {

    private static final String KEY = "shihuo-repl-key!";

    private Crypto() {
    }

    public static String aesEncryptBase64(String plain) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(KEY.getBytes("UTF-8"), "AES"));
        return Base64.encodeToString(cipher.doFinal(plain.getBytes("UTF-8")), Base64.NO_WRAP);
    }

    public static String aesDecryptBase64(String cipherText) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(KEY.getBytes("UTF-8"), "AES"));
        return new String(cipher.doFinal(Base64.decode(cipherText, Base64.NO_WRAP)), "UTF-8");
    }
}
