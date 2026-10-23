/*
 * 04_skip_interceptor.js —— 复刻课件 6.4.2 节：把加密拦截器改成空实现，明文直发。
 *
 * 用法（App 已启动）：frida -U -n 识货复刻 -l 04_skip_interceptor.js
 * 预期：
 *   - 日志打印拦截器清单；
 *   - 点"详情（老接口·加密）"时不再输出"请求加密"，服务端收到 goods_id 明文；
 *   - 连点 4 次后服务端返回 status=428 图片验证码（复刻课件的验证码环节）。
 * 仅限学习研究，禁止商用。
 */
Java.perform(function () {
    var Builder = Java.use("okhttp3.OkHttpClient$Builder");
    Builder.addInterceptor.implementation = function (interceptor) {
        try {
            console.log("[interceptor] " + interceptor.$className);
        } catch (e) {
            console.log("[interceptor] <取类名失败>");
        }
        return this.addInterceptor.overload("okhttp3.Interceptor").call(this, interceptor);
    };

    var Enc = Java.use("com.repl.shihuo.net.EncryptInterceptor");
    Enc.intercept.implementation = function (chain) {
        console.log("[hook] 跳过 EncryptInterceptor，明文直发 " + chain.request().url());
        return chain.proceed(chain.request());
    };
    console.log("[*] 已把 EncryptInterceptor.intercept 改成 chain.proceed(chain.request())");
});
