/*
 * 复刻 day19 路线 B 的前半段：hook art 的 RegisterNatives，
 * 拿到动态注册的 name / signature / fnPtr，并换算成「模块基址 + 偏移」。
 * 真实样本里这一步得到 s (Ljava/util/SortedMap;)Lcom/bilibili/nativelibrary/SignedQuery; offset 0x1c97
 */
function hookRegisterNatives() {
    var symbols = Module.enumerateSymbolsSync("libart.so");
    var targets = [];
    var seen = {};
    for (var i = 0; i < symbols.length; i++) {
        var name = symbols[i].name;
        if (name.indexOf("RegisterNatives") < 0) continue;
        if (name.indexOf("CheckJNI") >= 0) continue;
        var key = symbols[i].address.toString();
        if (seen[key]) continue;
        seen[key] = true;
        targets.push(symbols[i]);
        console.log("[*] symbol = " + name + " @" + symbols[i].address);
    }
    if (targets.length === 0) {
        console.log("[!] RegisterNatives symbol not found");
        return;
    }

    var pointerSize = Process.pointerSize;
    targets.forEach(function (target) {
        Interceptor.attach(target.address, {
            onEnter: function (args) {
                var env = Java.vm.tryGetEnv();
                if (env === null) return;
                var className;
                try {
                    className = env.getClassName(args[1]);
                } catch (e) {
                    return;
                }
                if (className.indexOf("BiliSign") < 0) return;

                var methods = args[2];
                var count = args[3].toInt32();
                console.log("[RegisterNatives] class=" + className + " count=" + count);
                for (var i = 0; i < count; i++) {
                    var base = methods.add(i * pointerSize * 3);
                    var namePtr = base.readPointer();
                    var sigPtr = base.add(pointerSize).readPointer();
                    var fnPtr = base.add(pointerSize * 2).readPointer();
                    var mod = Process.findModuleByAddress(fnPtr);
                    var offset = mod === null ? "?" : "0x" + fnPtr.sub(mod.base).toString(16);
                    console.log("  name=" + namePtr.readCString()
                        + " sig=" + sigPtr.readCString()
                        + " module=" + (mod === null ? "?" : mod.name)
                        + " offset=" + offset);
                }
            }
        });
    });
    console.log("[*] RegisterNatives hooks installed: " + targets.length);
}

// 必须放在 Java.perform 里：VM 就绪后 Java.vm.tryGetEnv() 才可用
Java.perform(hookRegisterNatives);
