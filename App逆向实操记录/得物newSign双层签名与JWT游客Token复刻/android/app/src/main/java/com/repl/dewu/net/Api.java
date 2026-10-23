package com.repl.dewu.net;

public class Api {
    public static final String UA = "duapp/4.74.5(android;11)";
    public static final String VERSION = "4.74.5";

    public static String version() {
        return BuildConfigUrl.BASE + "/app/version";
    }

    public static String visitorToken() {
        return BuildConfigUrl.BASE + "/api/v1/app/user_core/users/getVisitorUserId";
    }

    public static String feed() {
        return BuildConfigUrl.BASE + "/sns-rec/v1/recommend/all/feed";
    }

    public static String ping() {
        return BuildConfigUrl.BASE + "/app/ping";
    }

    /** 单独抽出来，避免在纯 Java 文件里到处 import BuildConfig */
    public static class BuildConfigUrl {
        public static final String BASE = com.repl.dewu.BuildConfig.BASE_URL;
    }
}
