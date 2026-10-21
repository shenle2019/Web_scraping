package com.shenjiahang.netapp;

import android.app.Application;
import android.content.Context;

/**
 * 只做一件事：把 Application 的 Context 暴露给拦截器读 token。
 */
public class App extends Application {

    private static Context appContext;

    @Override
    public void onCreate() {
        super.onCreate();
        appContext = this;
    }

    public static Context ctx() {
        return appContext;
    }
}
