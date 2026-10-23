/*
 * 03_list_interceptors.js —— 复刻课件 6.3 节：Hook OkHttpClient$Builder.addInterceptor 列出所有拦截器。
 *
 * 用法（App 已启动）：frida -U -n 识货复刻 -l 03_list_interceptors.js
 * 预期：打印 com.repl.shihuo.net.EncryptInterceptor 等类名，为下一步定位加密逻辑提供入口。
 * 仅限学习研究，禁止商用。
 */
Java.perform(function () {
    var Builder = Java.use("okhttp3.OkHttpClient$Builder");
    Builder.addInterceptor.implementation = function (interceptor) {
        try {
            console.log("[interceptor] " + interceptor.$className);
        } catch (e) {
            console.log("[interceptor] <取类名失败 " + e + ">");
        }
        return this.addInterceptor.overload("okhttp3.Interceptor").call(this, interceptor);
    };
    console.log("[*] 已 Hook OkHttpClient$Builder.addInterceptor");
});
