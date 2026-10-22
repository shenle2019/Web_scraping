package com.autohome.ahkit.utils;

import android.content.Context;
import android.util.Base64;

import com.autohome.ahkit.AHAPIHelper;

import java.security.MessageDigest;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * 复刻自车智赢 3.56.0 的 com.autohome.ahkit.utils.SecurityUtil。
 * 只保留登录链路用到的两个算法：MD5 与 3DES。
 */
public class SecurityUtil {

    private static final char[] HEX = "0123456789ABCDEF".toCharArray();
    private static final String IV = "appapich";

    public static String encodeMD5(String plain) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(plain.getBytes("UTF-8"));
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(HEX[(b >>> 4) & 15]);
                sb.append(HEX[b & 15]);
            }
            return sb.toString().toLowerCase();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public static String encode3Des(Context context, String plain) {
        try {
            String key = AHAPIHelper.getDesKey(context);
            byte[] keyBytes = new byte[24];
            System.arraycopy(key.getBytes("UTF-8"), 0, keyBytes, 0, 24);
            Cipher cipher = Cipher.getInstance("desede/CBC/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE,
                    new SecretKeySpec(keyBytes, "DESede"),
                    new IvParameterSpec(IV.getBytes("UTF-8")));
            return encode(cipher.doFinal(plain.getBytes("UTF-8")));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static String encode(byte[] data) {
        return Base64.encodeToString(data, Base64.NO_WRAP);
    }
}
