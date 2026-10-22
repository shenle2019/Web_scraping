package com.che168.atclibrary.base;

import com.autohome.ahkit.bean.SignType;
import com.autohome.ahkit.utils.SecurityUtil;
import java.util.Locale;
import java.util.TreeMap;
import kotlin.Metadata;
import kotlin.jvm.internal.Intrinsics;
/* compiled from: SignManager.kt */
@Metadata(d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0005\n\u0002\u0010\b\n\u0000\n\u0002\u0018\u0002\n\u0000\bÆ\u0002\u0018\u00002\u00020\u0001B\u0007\b\u0002¢\u0006\u0002\u0010\u0002J$\u0010\b\u001a\u00020\u00042\b\b\u0001\u0010\t\u001a\u00020\n2\u0012\u0010\u000b\u001a\u000e\u0012\u0004\u0012\u00020\u0004\u0012\u0004\u0012\u00020\u00040\fR\u000e\u0010\u0003\u001a\u00020\u0004X\u0086T¢\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0086T¢\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0004X\u0086T¢\u0006\u0002\n\u0000R\u000e\u0010\u0007\u001a\u00020\u0004X\u0086T¢\u0006\u0002\n\u0000¨\u0006\r"}, d2 = {"Lcom/che168/atclibrary/base/SignManager;", "", "()V", "KEY_AUTOHOME", "", "KEY_SHARE", "KEY_V1", "KEY_V2", "signByType", "signType", "", "paramMap", "Ljava/util/TreeMap;", "ATCLibrary_release"}, k = 1, mv = {1, 6, 0}, xi = 48)
/* loaded from: E:\路飞学城\课件\APP逆向(12期)\_repl_day14_chezhiying\apk_unpack\dex\classes2.dex */
public final class SignManager {
    public static final SignManager INSTANCE = new SignManager();
    public static final String KEY_AUTOHOME = "@7U$aPOE@$";
    public static final String KEY_SHARE = "moc.861ehc.relaed.bup.wyfv";
    public static final String KEY_V1 = "com.che168.www";
    public static final String KEY_V2 = "W@oC!AH_6Ew1f6%8";

    private SignManager() {
    }

    public final String signByType(@SignType int i, TreeMap<String, String> treeMap) {
        Intrinsics.checkNotNullParameter(treeMap, "paramMap");
        StringBuilder sb = new StringBuilder();
        String str = KEY_V1;
        if (i != 0) {
            if (i == 1) {
                str = KEY_V2;
            } else if (i == 2) {
                str = KEY_SHARE;
            } else if (i == 3) {
                str = KEY_AUTOHOME;
            }
        }
        sb.append(str);
        for (String str2 : treeMap.keySet()) {
            sb.append(str2);
            sb.append(treeMap.get(str2));
        }
        sb.append(str);
        String encodeMD5 = SecurityUtil.encodeMD5(sb.toString());
        if (encodeMD5 != null) {
            Locale locale = Locale.ROOT;
            Intrinsics.checkNotNullExpressionValue(locale, "ROOT");
            String upperCase = encodeMD5.toUpperCase(locale);
            Intrinsics.checkNotNullExpressionValue(upperCase, "this as java.lang.String).toUpperCase(locale)");
            if (upperCase != null) {
                return upperCase;
            }
        }
        return "";
    }
}
