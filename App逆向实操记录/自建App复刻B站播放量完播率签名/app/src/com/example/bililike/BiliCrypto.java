package com.example.bililike;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * 复刻课件里散落在三个类中的密码学部分：
 *  - com.bilibili.commons.m.a.g       -> sha256(明文 ‖ 盐)
 *  - t3.a.i.a.a.a.b.e.a               -> AES/CBC/PKCS5Padding
 *  - com.bilibili.droid.g0.a.i        -> Cipher.doFinal
 *
 * 仅学习研究使用，不连接任何线上服务。
 */
public final class BiliCrypto {

    /** day17 hook com.bilibili.commons.m.a.g 拿到的盐 */
    public static final String SHA256_SALT = "9cafa6466a028bfb";
    /** day17 hook SecretKeySpec 拿到的 key（32 字符 -> AES-256） */
    public static final String AES_KEY = "fd6b639dbcff0c2a1b03b389ec763c4b";
    /** day17 hook IvParameterSpec 拿到的 iv（16 字节） */
    public static final String AES_IV = "77b07a672d57d64c";
    /** day19 hook so 内 update 拿到的四段盐拼起来 */
    public static final String MD5_SALT = "560c52ccd288fed045859ed18bffd973";

    private BiliCrypto() {
    }

    public static String hex(byte[] data) {
        char[] digits = "0123456789abcdef".toCharArray();
        char[] out = new char[data.length * 2];
        for (int i = 0; i < data.length; i++) {
            int v = data[i] & 0xFF;
            out[i * 2] = digits[v >>> 4];
            out[i * 2 + 1] = digits[v & 0x0F];
        }
        return new String(out);
    }

    public static byte[] randomBytes(int len) {
        byte[] b = new byte[len];
        new java.util.Random().nextBytes(b);
        return b;
    }

    public static String md5Hex(String str) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            return hex(md.digest(str.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /** 对应 com.bilibili.commons.m.a.g：先 update 明文，再 update 盐，不是 HMAC */
    public static String sha256Hex(byte[] plain, byte[] salt) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA256");
            md.update(plain);
            md.update(salt);
            return hex(md.digest());
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public static String sha1Hex(String str) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA1");
            return hex(md.digest(str.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /** 对应 t3.a.i.a.a.a.b.e.a：整体 AES，失败时真实 App 会退化返回明文 */
    public static byte[] aesEncrypt(String plain) {
        try {
            SecretKeySpec key = new SecretKeySpec(
                    AES_KEY.getBytes(StandardCharsets.UTF_8), "AES");
            IvParameterSpec iv = new IvParameterSpec(
                    AES_IV.getBytes(StandardCharsets.UTF_8));
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE, key, iv);
            return cipher.doFinal(plain.getBytes(StandardCharsets.UTF_8));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * fp_local 尾部校验码：g=0、h=60、step=2，每两位按 hex 解析后累加，取模 256。
     * 对应课件 hook kotlin.g0.q.S0 拿到的固定区间。
     */
    public static String fpChecksum(String str) {
        int limit = Math.min(str.length() - 1, 62);
        int sum = 0;
        for (int i = 0; i <= limit - 2; i += 2) {
            sum += Integer.parseInt(str.substring(i, i + 2), 16) & 0xFF;
        }
        return String.format(java.util.Locale.US, "%02x", sum % 256);
    }
}
