/*
 * 复刻 day19 路线 B 的兜底手法：hook libart.so 的 NewStringUTF，
 * 过滤长度 32 的串（MD5 hex），并打印 backtrace 看调用方。
 */
Java.perform(function () {
    var symbols = Module.enumerateSymbolsSync("libart.so");
    var target = null;
    for (var i = 0; i < symbols.length; i++) {
        var name = symbols[i].name;
        if (name.indexOf("NewStringUTF") >= 0 && name.indexOf("CheckJNI") < 0) {
            target = symbols[i];
            console.log("[*] symbol = " + name + " @" + target.address);
            break;
        }
    }
    if (target === null) {
        console.log("[!] NewStringUTF not found");
        return;
    }

    Interceptor.attach(target.address, {
        onEnter: function (args) {
            var str = args[1].readCString();
            if (str === null || str.length !== 32) return;
            if (!/^[0-9a-f]{32}$/.test(str)) return;
            console.log("[NewStringUTF] " + str);
            console.log(Thread.backtrace(this.context, Backtracer.ACCURATE)
                .map(DebugSymbol.fromAddress).slice(0, 5).join("\n"));
        }
    });
    console.log("[*] NewStringUTF hook installed");
});
