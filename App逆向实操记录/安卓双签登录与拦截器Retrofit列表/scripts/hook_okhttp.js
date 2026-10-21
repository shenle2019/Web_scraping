/*
 * 仅限学习研究，禁止商用。
 * 目标：验证 App 的签名头不是业务代码写的，而是 OkHttp 拦截器统一注入。
 *
 * 思路：hook RealInterceptorChain.proceed(Request)，在请求真正发出去之前
 * 把 method / url / 全部 header / body 打出来。能在这里看到 ctime、hsign、
 * Authorization，就说明拦截器生效了。
 *
 * 注意：OkHttp 3.x 的类名是 okhttp3.RealInterceptorChain，
 *       4.x（本工程 4.9.1）挪到了 okhttp3.internal.http.RealInterceptorChain，
 *       直接按 3.x 的包名 hook 会报 ClassNotFoundException。
 */
Java.perform(function () {
    var TAG = "[frida]";

    var candidates = [
        "okhttp3.internal.http.RealInterceptorChain",   // OkHttp 4.x
        "okhttp3.RealInterceptorChain"                  // OkHttp 3.x
    ];
    var Chain = null;
    for (var i = 0; i < candidates.length; i++) {
        try {
            Chain = Java.use(candidates[i]);
            console.log(TAG + " chain class = " + candidates[i]);
            break;
        } catch (e) {
            // 换下一个候选
        }
    }
    if (Chain === null) {
        console.log(TAG + " RealInterceptorChain 未找到，检查 OkHttp 版本");
        return;
    }

    function dump(headers) {
        for (var i = 0; i < headers.size(); i++) {
            console.log(TAG + "   " + headers.name(i) + ": " + headers.value(i));
        }
    }

    Chain.proceed.overload("okhttp3.Request").implementation = function (request) {
        try {
            console.log("\n" + TAG + " >>> " + request.method() + " " + request.url().toString());
            dump(request.headers());

            var body = request.body();
            if (body !== null) {
                var Buffer = Java.use("okio.Buffer");
                var buffer = Buffer.$new();
                body.writeTo(buffer);
                console.log(TAG + "   body: " + buffer.readUtf8().replace(/\n/g, "&"));
            }
        } catch (e) {
            console.log(TAG + " dump error: " + e);
        }
        return this.proceed(request);
    };

    // 注：OkHttpClient$Builder.addInterceptor 在 frida-java-bridge 里不能直接
    // 取方法引用（TypeError: not a function），所以这里只验证“请求发出前的真实请求头”，
    // 拦截器是否挂上由 url/header 里出现 ctime、hsign 反推。

    console.log(TAG + " hooked proceed");
});
