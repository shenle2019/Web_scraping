package com.shenjiahang.netapp.net;

import com.shenjiahang.netapp.util.Md5Utils;

/**
 * 两级签名口径，和课件里的思路一致但参数排布按本案例重新设计：
 * <pre>
 * body   sign = md5(t1 + user + md5(pwd))
 * header hsign = md5(ctime + salt)
 * </pre>
 * 抓包时同时能看到 t1 和 ctime，可以据此反推口径。
 */
public final class Signer {

    private Signer() {
    }

    /** 表单签名：t1 为秒级时间戳 */
    public static String bodySign(String user, String rawPwd, String t1) {
        return Md5Utils.md5(t1 + user + Md5Utils.md5(rawPwd));
    }

    /** 请求头签名：ctime 为秒级时间戳 */
    public static String headerSign(String ctime) {
        return Md5Utils.md5(ctime + NetConfig.SALT);
    }

    public static String nowSeconds() {
        return String.valueOf(System.currentTimeMillis() / 1000L);
    }
}
