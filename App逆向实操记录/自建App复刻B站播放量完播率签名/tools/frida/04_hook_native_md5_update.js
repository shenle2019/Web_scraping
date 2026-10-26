/*
 * 复刻 day19 的 sub_22B0：hook so 内的 MD5 update，按「基址 + 偏移」打印每一段入参。
 * 真实样本：Module.findBaseAddress("libbili.so").add(0x22b0 + 1)
 * 本复刻工程的函数是导出符号 bili_md5_update，偏移由脚本现场算出来打印。
 */
function main() {
    var mod = Process.findModuleByName("libbili.so");
    if (mod === null) {
        console.log("[!] libbili.so not loaded yet");
        return;
    }
    var fn = Module.getExportByName("libbili.so", "bili_md5_update");
    var offset = fn.sub(mod.base);
    console.log("[*] libbili.so base=" + mod.base + " update=" + fn
        + " offset=0x" + offset.toString(16)
        + "（本工程导出符号的偏移；对照课件真实样本 sub_22B0，thumb 指令需 +1）");

    Interceptor.attach(fn, {
        onEnter: function (args) {
            var len = args[2].toInt32();
            var text = null;
            try {
                var s = args[1].readUtf8String(len);
                // 只保留可打印 ASCII，过滤 md5_final 里的 0x80 填充与长度位
                if (s !== null && /^[\x09\x0a\x0d\x20-\x7e]*$/.test(s)) text = s;
            } catch (e) {
                text = null;
            }
            if (text === null) {
                console.log("[update][binary] len=" + len + " (填充/长度位，忽略)");
                return;
            }
            if (len === 8) {
                console.log("[update][salt ] len=8 " + text);
            } else {
                console.log("[update][plain] len=" + len + " "
                    + text.substring(0, 80) + (len > 80 ? "..." : ""));
            }
        }
    });
    console.log("[*] update hook installed");
}

setImmediate(function () {
    // 等 System.loadLibrary 完成后再挂
    var tries = 0;
    var timer = setInterval(function () {
        var mod = Process.findModuleByName("libbili.so");
        if (mod !== null || tries++ > 50) {
            clearInterval(timer);
            main();
        }
    }, 100);
});
