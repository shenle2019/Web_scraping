package com.example.bililike;

import android.content.Context;
import android.provider.Settings;
import android.util.Base64;

import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.UUID;

/**
 * 复刻 day18 的四个设备指纹 + 复用 day17 的 did 生成。
 *
 * 真机取值顺序与课件一致：mac|蓝牙|设备总线|sn -> 异或链 -> Base64；
 * 取不到硬件信息时（模拟器/权限受限）退化成 android_id@MD5(model)。
 */
public final class DeviceProfile {

    public final String mac;
    public final String androidId;
    public final String model;
    public final String band;

    public final String deviceId;
    public final String buvid;
    public final String sessionId;
    public final String fpLocal;
    public final String fpRemote;

    private DeviceProfile(Context ctx) {
        this.mac = randomMac();
        this.model = android.os.Build.MODEL == null ? "" : android.os.Build.MODEL;
        this.band = android.os.Build.BRAND == null ? "" : android.os.Build.BRAND;
        String aid = "unknown";
        try {
            aid = Settings.Secure.getString(ctx.getContentResolver(),
                    Settings.Secure.ANDROID_ID);
        } catch (Exception ignored) {
        }
        this.androidId = aid == null ? "" : aid;

        this.deviceId = buildDeviceId(this.mac, "", "", randomSn(), this.androidId, this.model);
        this.buvid = buildBuvid(this.androidId);
        this.sessionId = BiliCrypto.hex(BiliCrypto.randomBytes(4));
        this.fpLocal = buildFingerprint(this.buvid, this.model, this.band);
        this.fpRemote = buildFingerprint(this.buvid, this.model, this.band);
    }

    public static DeviceProfile create(Context ctx) {
        return new DeviceProfile(ctx);
    }

    private static String randomMac() {
        byte[] b = BiliCrypto.randomBytes(6);
        b[0] = (byte) ((b[0] | 0x02) & 0xFE); // 本地管理地址，避免撞真实网卡
        return BiliCrypto.hex(b);
    }

    private static String randomSn() {
        return BiliCrypto.hex(BiliCrypto.randomBytes(8)).toUpperCase(Locale.US);
    }

    /** did：mac|蓝牙|设备总线|sn -> 首字节异或长度 -> 链式异或 -> Base64 去等号 */
    public static String buildDeviceId(String mac, String bt, String bus, String sn,
                                       String androidId, String model) {
        String raw = mac + "|" + bt + "|" + bus + "|" + sn;
        if (raw.length() < 4) {
            raw = androidId + "@" + BiliCrypto.md5Hex(model);
        }
        byte[] data = raw.getBytes(StandardCharsets.UTF_8);
        data[0] ^= (byte) (data.length & 0xFF);
        for (int i = 1; i < data.length; i++) {
            data[i] ^= data[i - 1];
        }
        return Base64.encodeToString(data, Base64.NO_WRAP | Base64.NO_PADDING);
    }

    /** buvid：XW + md5[2] + md5[12] + md5[22] + md5，整体大写 */
    public static String buildBuvid(String seed) {
        String uuid = UUID.randomUUID().toString().replace("-", "");
        String md5 = BiliCrypto.md5Hex(uuid + seed);
        String buvid = "XW" + md5.charAt(2) + md5.charAt(12) + md5.charAt(22) + md5;
        return buvid.toUpperCase(Locale.US);
    }

    /** fp_local：hex(md5(buvid+model+band)) + yyyyMMddHHmmss + hex(8随机字节) + 校验码 */
    public static String buildFingerprint(String buvid, String model, String band) {
        String head = BiliCrypto.md5Hex(buvid + model + band);
        String ts = new SimpleDateFormat("yyyyMMddHHmmss", Locale.US).format(new Date());
        String rand = BiliCrypto.hex(BiliCrypto.randomBytes(8));
        String str2 = head + ts + rand;
        return str2 + BiliCrypto.fpChecksum(str2);
    }
}
