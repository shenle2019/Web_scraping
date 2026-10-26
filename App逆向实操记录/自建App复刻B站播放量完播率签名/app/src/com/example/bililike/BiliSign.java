package com.example.bililike;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * 复刻 day19 的 so 层入口：com.bilibili.nativelibrary.LibBili.s(SortedMap)。
 *
 * nativeSign 在 libbili.so（libbili-sign 工程）里通过 RegisterNatives 动态注册，
 * 导出表里没有 Java_com_example_bililike_BiliSign_nativeSign，只能靠 hook
 * RegisterNatives 拿函数偏移。
 */
public final class BiliSign {

    static {
        // 课件里是 Relinker.c.c("bili")，本质都是 System.loadLibrary
        System.loadLibrary("bili");
    }

    private BiliSign() {
    }

    public static native String nativeSign(String plain);

    /** Java 侧同算法实现，用于自检 native 结果是否一致 */
    public static String javaSign(String plain) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            md.update(plain.getBytes(StandardCharsets.UTF_8));
            md.update("560c52cc".getBytes(StandardCharsets.UTF_8));
            md.update("d288fed0".getBytes(StandardCharsets.UTF_8));
            md.update("45859ed1".getBytes(StandardCharsets.UTF_8));
            md.update("8bffd973".getBytes(StandardCharsets.UTF_8));
            return BiliCrypto.hex(md.digest());
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /** Python 侧参考值：md5(plain + 四段盐) */
    public static String expectedSign(String plain) {
        return BiliCrypto.md5Hex(plain + BiliCrypto.MD5_SALT);
    }
}
