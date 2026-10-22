package com.autohome.ahkit.utils;

import android.content.Context;
import android.text.TextUtils;
import com.autohome.ahkit.AHAPIHelper;
import com.autohome.ums.common.network.HttpUtils;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.DESedeKeySpec;
import javax.crypto.spec.IvParameterSpec;
/* loaded from: E:\路飞学城\课件\APP逆向(12期)\_repl_day14_chezhiying\apk_unpack\dex\classes.dex */
public class SecurityUtil {
    private static final String encoding = "UTF-8";
    private static final String iv = "appapich";
    private static final char[] legalChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".toCharArray();

    public static String encode3Des(Context context, String str) {
        String desKey = AHAPIHelper.getDesKey(context);
        byte[] bArr = null;
        if (TextUtils.isEmpty(desKey)) {
            return null;
        }
        try {
            SecretKey generateSecret = SecretKeyFactory.getInstance("desede").generateSecret(new DESedeKeySpec(desKey.getBytes()));
            Cipher cipher = Cipher.getInstance("desede/CBC/PKCS5Padding");
            cipher.init(1, generateSecret, new IvParameterSpec(iv.getBytes()));
            bArr = cipher.doFinal(str.getBytes("UTF-8"));
        } catch (Exception unused) {
        }
        return encode(bArr).toString();
    }

    public static String decode3Des(Context context, String str) {
        String desKey = AHAPIHelper.getDesKey(context);
        if (TextUtils.isEmpty(desKey)) {
            return null;
        }
        try {
            SecretKey generateSecret = SecretKeyFactory.getInstance("desede").generateSecret(new DESedeKeySpec(desKey.getBytes()));
            Cipher cipher = Cipher.getInstance("desede/CBC/PKCS5Padding");
            cipher.init(2, generateSecret, new IvParameterSpec(iv.getBytes()));
            return new String(cipher.doFinal(decode(str)), "UTF-8");
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public static final String encodeMD5(String str) {
        char[] cArr = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
        try {
            byte[] bytes = str.getBytes();
            MessageDigest messageDigest = MessageDigest.getInstance("MD5");
            messageDigest.update(bytes);
            byte[] digest = messageDigest.digest();
            char[] cArr2 = new char[digest.length * 2];
            int i = 0;
            for (byte b : digest) {
                int i2 = i + 1;
                cArr2[i] = cArr[(b >>> 4) & 15];
                i = i2 + 1;
                cArr2[i2] = cArr[b & 15];
            }
            return new String(cArr2).toLowerCase();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public static String md5Code(String str) {
        try {
            String bigInteger = new BigInteger(1, MessageDigest.getInstance("md5").digest(str.getBytes())).toString(16);
            for (int i = 0; i < 32 - bigInteger.length(); i++) {
                bigInteger = "0" + bigInteger;
            }
            return bigInteger;
        } catch (NoSuchAlgorithmException unused) {
            throw new RuntimeException("没有md5这个算法！");
        }
    }

    public static String encode(byte[] bArr) {
        int length = bArr.length;
        StringBuffer stringBuffer = new StringBuffer((bArr.length * 3) / 2);
        int i = length - 3;
        int i2 = 0;
        loop0: while (true) {
            int i3 = 0;
            while (i2 <= i) {
                int i4 = ((bArr[i2] & 255) << 16) | ((bArr[i2 + 1] & 255) << 8) | (bArr[i2 + 2] & 255);
                char[] cArr = legalChars;
                stringBuffer.append(cArr[(i4 >> 18) & 63]);
                stringBuffer.append(cArr[(i4 >> 12) & 63]);
                stringBuffer.append(cArr[(i4 >> 6) & 63]);
                stringBuffer.append(cArr[i4 & 63]);
                i2 += 3;
                int i5 = i3 + 1;
                if (i3 >= 14) {
                    break;
                }
                i3 = i5;
            }
            stringBuffer.append(" ");
        }
        int i6 = 0 + length;
        if (i2 == i6 - 2) {
            int i7 = ((bArr[i2 + 1] & 255) << 8) | ((bArr[i2] & 255) << 16);
            char[] cArr2 = legalChars;
            stringBuffer.append(cArr2[(i7 >> 18) & 63]);
            stringBuffer.append(cArr2[(i7 >> 12) & 63]);
            stringBuffer.append(cArr2[(i7 >> 6) & 63]);
            stringBuffer.append(HttpUtils.EQUAL_SIGN);
        } else if (i2 == i6 - 1) {
            int i8 = (bArr[i2] & 255) << 16;
            char[] cArr3 = legalChars;
            stringBuffer.append(cArr3[(i8 >> 18) & 63]);
            stringBuffer.append(cArr3[(i8 >> 12) & 63]);
            stringBuffer.append("==");
        }
        return stringBuffer.toString();
    }

    private static int decode(char c) {
        int i;
        if (c < 'A' || c > 'Z') {
            if (c >= 'a' && c <= 'z') {
                i = c - 'a';
            } else if (c < '0' || c > '9') {
                if (c != '+') {
                    if (c != '/') {
                        if (c == '=') {
                            return 0;
                        }
                        throw new RuntimeException("unexpected code: " + c);
                    }
                    return 63;
                }
                return 62;
            } else {
                i = (c - '0') + 26;
            }
            return i + 26;
        }
        return c - 'A';
    }

    public static byte[] decode(String str) {
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        try {
            decode(str, byteArrayOutputStream);
            byte[] byteArray = byteArrayOutputStream.toByteArray();
            try {
                byteArrayOutputStream.close();
            } catch (IOException e) {
                PrintStream printStream = System.err;
                printStream.println("Error while decoding BASE64: " + e.toString());
            }
            return byteArray;
        } catch (IOException unused) {
            throw new RuntimeException();
        }
    }

    private static void decode(String str, OutputStream outputStream) throws IOException {
        int length = str.length();
        int i = 0;
        while (true) {
            if (i < length && str.charAt(i) <= ' ') {
                i++;
            } else if (i == length) {
                return;
            } else {
                int i2 = i + 2;
                int i3 = i + 3;
                int decode = (decode(str.charAt(i)) << 18) + (decode(str.charAt(i + 1)) << 12) + (decode(str.charAt(i2)) << 6) + decode(str.charAt(i3));
                outputStream.write((decode >> 16) & 255);
                if (str.charAt(i2) == '=') {
                    return;
                }
                outputStream.write((decode >> 8) & 255);
                if (str.charAt(i3) == '=') {
                    return;
                }
                outputStream.write(decode & 255);
                i += 4;
            }
        }
    }
}
