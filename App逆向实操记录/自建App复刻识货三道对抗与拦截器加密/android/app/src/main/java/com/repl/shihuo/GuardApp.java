package com.repl.shihuo;

import android.app.Application;

import com.repl.shihuo.security.FridaGuard;

/**
 * 复刻课件里"App 一启动就检测 Frida"的行为：
 * 进程创建后第一件事就是加载检测 so，命中就退出。
 */
public class GuardApp extends Application {

    @Override
    public void onCreate() {
        super.onCreate();
        FridaGuard.check();
    }
}
