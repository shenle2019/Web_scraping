/*
 * 复刻 day17 的取 key / iv / 盐 手法：
 *   - hook javax.crypto.spec.SecretKeySpec(byte[], String) -> AES key
 *   - hook javax.crypto.spec.IvParameterSpec(byte[])      -> AES iv
 *   - hook com.bilibili.commons.m.a.g 的等价物 sha256Hex -> SHA256 盐
 */
function bytesToStr(arr) {
    var s = "";
    for (var i = 0; i < arr.length; i++) {
        s += String.fromCharCode(arr[i] & 0xff);
    }
    return s;
}

function bytesToHex(arr) {
    var s = "";
    for (var i = 0; i < arr.length; i++) {
        var v = arr[i] & 0xff;
        s += (v < 16 ? "0" : "") + v.toString(16);
    }
    return s;
}

Java.perform(function () {
    var SecretKeySpec = Java.use("javax.crypto.spec.SecretKeySpec");
    SecretKeySpec.$init.overload("[B", "java.lang.String").implementation = function (key, alg) {
        console.log("[SecretKeySpec] alg=" + alg + " key=" + bytesToStr(key));
        return this.$init(key, alg);
    };

    var IvParameterSpec = Java.use("javax.crypto.spec.IvParameterSpec");
    IvParameterSpec.$init.overload("[B").implementation = function (iv) {
        console.log("[IvParameterSpec] iv=" + bytesToStr(iv) + " hex=" + bytesToHex(iv));
        return this.$init(iv);
    };

    var BiliCrypto = Java.use("com.example.bililike.BiliCrypto");
    BiliCrypto.sha256Hex.implementation = function (plain, salt) {
        var sign = this.sha256Hex(plain, salt);
        console.log("[sha256Hex] salt=" + bytesToStr(salt));
        console.log("[sha256Hex] plain=" + bytesToStr(plain).substring(0, 100) + "...");
        console.log("[sha256Hex] sign=" + sign);
        return sign;
    };

    console.log("[*] crypto hooks installed");
});
