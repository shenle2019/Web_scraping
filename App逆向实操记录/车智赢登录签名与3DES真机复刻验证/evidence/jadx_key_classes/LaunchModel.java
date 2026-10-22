package com.che168.autotradercloud.launch.model;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import androidx.core.app.NotificationManagerCompat;
import com.autohome.ahkit.okhttp3.OkHttpUrlLoader;
import com.autohome.ahkit.utils.EmptyUtil;
import com.autohome.ucbrand.db.CarDBManager;
import com.bumptech.glide.Glide;
import com.bumptech.glide.load.model.GlideUrl;
import com.che168.ahnetwork.http.HttpUtil;
import com.che168.ahnetwork.http.OkHttpClientProvider;
import com.che168.ahnetwork.http.interceptor.HeadersInterceptor;
import com.che168.ahnetwork.http.interceptor.HostInterceptor;
import com.che168.ahnetwork.http.interceptor.ParamsInterceptor;
import com.che168.ahuikit.webview.ATCWebView;
import com.che168.atclibrary.base.SignManager;
import com.che168.atclibrary.provider.ContextProvider;
import com.che168.atclibrary.utils.ATCEmptyUtil;
import com.che168.atclibrary.utils.GsonUtil;
import com.che168.atclibrary.utils.LogUtil;
import com.che168.atclibrary.utils.SystemUtil;
import com.che168.autotradercloud.Constants;
import com.che168.autotradercloud.R;
import com.che168.autotradercloud.base.CrashHandler;
import com.che168.autotradercloud.base.cookies.ATCCookiesManager;
import com.che168.autotradercloud.base.httpNew.ApiException;
import com.che168.autotradercloud.base.httpNew.BaseModel;
import com.che168.autotradercloud.base.httpNew.BaseResult;
import com.che168.autotradercloud.base.httpNew.ResponseCallback;
import com.che168.autotradercloud.base.push.GeTuiPushService;
import com.che168.autotradercloud.base.push.ReceivePushService;
import com.che168.autotradercloud.gold_bar.model.GoldModel;
import com.che168.autotradercloud.launch.LocalPushReceiver;
import com.che168.autotradercloud.launch.bean.AppImageBean;
import com.che168.autotradercloud.launch.constant.LaunchConstants;
import com.che168.autotradercloud.my.model.AddressBookModel;
import com.che168.autotradercloud.statistics.BaseAnalytics;
import com.che168.autotradercloud.systest.SystemTestModel;
import com.che168.autotradercloud.user.model.UserModel;
import com.che168.autotradercloud.util.AppUtils;
import com.che168.autotradercloud.util.HostHelp;
import com.che168.autotradercloud.util.NetworkStatisticsUtil;
import com.che168.autotradercloud.util.SPUtils;
import com.che168.autotradercloud.util.UserConfigUtil;
import com.che168.autotradercloud.web.model.WebViewModel;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.reflect.TypeToken;
import com.igexin.sdk.PushManager;
import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.Calendar;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import okhttp3.Cookie;
import okhttp3.CookieJar;
import okhttp3.HttpUrl;
import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Response;
/* loaded from: E:\路飞学城\课件\APP逆向(12期)\_repl_day14_chezhiying\apk_unpack\dex\classes2.dex */
public class LaunchModel extends BaseModel {
    private static final long DEFAULT_TIME_OUT = 15;
    private static final String HEADER_REFERER = "https://www.che168.com";
    private static final int INTERVAL = 86400000;
    public static final String KEY_APP_ID = "_appid";
    public static final String KEY_APP_VERSION = "appversion";
    public static final String KEY_CHANNEL_ID = "channelid";
    private static final String KEY_ONLINE_PARAMS = "key_online_param";
    public static final String KEY_SIGN = "_sign";
    public static final String KEY_UDID = "udid";
    public static final String KEY_USERKEY = "userkey";
    private static final String GET_APP_IMAGE = HostHelp.HOST_APICZY + "/private/v199/advert/indeximg";
    private static final String GET_ONLINE_PARAMS = HostHelp.HOST_APPS_API + "/phone/v57/app/onlineconfig.ashx";
    private static final List<String> HOST_WHITE_LIST = Arrays.asList("autohome.com.cn", "che168.com", "autoimg.cn", "ahkit.top", "saasbussinessapi.terra.corpautohome.com", "saasapi.test.che168.com", "saasapi.che168.com", "saasapi.lq.che168.com", "saasapi.pre.che168.com", "saasapi.che168.com");
    private static Map<String, String> mOnlineParams = null;

    /* loaded from: E:\路飞学城\课件\APP逆向(12期)\_repl_day14_chezhiying\apk_unpack\dex\classes2.dex */
    public interface ILoadOnlineParamsCallback {
        void callback(Map<String, String> map);
    }

    public static void initConfig() {
        CrashHandler crashHandler = CrashHandler.getInstance();
        crashHandler.init(SystemUtil.getAppName() + "_log");
        LogUtil.init(false);
        AddressBookModel.startSyn();
        PushManager.getInstance().initialize(ContextProvider.getContext(), GeTuiPushService.class);
        PushManager.getInstance().registerPushIntentService(ContextProvider.getContext(), ReceivePushService.class);
        UserConfigUtil.initUserConfig();
        CarDBManager.sCarDBResId = R.raw.cars_new;
        SystemTestModel.updateCarModelDB(ContextProvider.getContext());
        UserModel.loadDealerInfo();
        initImageLoad();
        if (UserModel.isLogin()) {
            UserModel.loadDealerSectionInfo();
        }
        loadOnlineParams(new ILoadOnlineParamsCallback() { // from class: com.che168.autotradercloud.launch.model.LaunchModel.1
            @Override // com.che168.autotradercloud.launch.model.LaunchModel.ILoadOnlineParamsCallback
            public void callback(Map<String, String> map) {
                String str;
                if (EmptyUtil.isEmpty(map) || (str = map.get("webcache")) == null) {
                    return;
                }
                ATCWebView.addUrlCommonParam("awbv", str);
            }
        });
        WebViewModel.updateOfflinePackage();
        statisticsPushClosed();
        if (UserModel.isLogin()) {
            ATCCookiesManager.INSTANCE.init();
        }
        if (UserModel.isLogin()) {
            GoldModel.INSTANCE.initGoldInfo();
        }
    }

    private static void statisticsPushClosed() {
        if (UserModel.isLogin()) {
            HashMap hashMap = new HashMap();
            hashMap.put("devicetoken", SPUtils.getClientId());
            hashMap.put("deviceid", SPUtils.getDeviceId());
            hashMap.put("open", NotificationManagerCompat.from(ContextProvider.getContext()).areNotificationsEnabled() ? "1" : "0");
            BaseAnalytics.commonClickEvent(ContextProvider.getContext(), "LaunchActivity", "c_app_czy_userset_pushstop", hashMap);
        }
    }

    public static void initTodayReportPush() {
        if (UserModel.isLogin()) {
            todayReportPush();
        }
    }

    private static void todayReportPush() {
        Context context = ContextProvider.getContext();
        Intent intent = new Intent(context, LocalPushReceiver.class);
        intent.setAction(LaunchConstants.ACTION_TODAY_REPORT);
        PendingIntent broadcast = PendingIntent.getBroadcast(context, 1001, intent, 268435456);
        AlarmManager alarmManager = (AlarmManager) context.getSystemService("alarm");
        Calendar calendar = Calendar.getInstance();
        calendar.set(11, 17);
        calendar.set(12, 0);
        calendar.set(13, 0);
        if (alarmManager == null) {
            return;
        }
        try {
            alarmManager.setRepeating(0, calendar.getTimeInMillis(), 86400000L, broadcast);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void initImageLoad() {
        OkHttpClient.Builder builder = new OkHttpClient.Builder();
        builder.addInterceptor(new Interceptor() { // from class: com.che168.autotradercloud.launch.model.LaunchModel.2
            public Response intercept(Interceptor.Chain chain) throws IOException {
                return chain.proceed(chain.request().newBuilder().header("referer", LaunchModel.HEADER_REFERER).build());
            }
        });
        Glide.get(ContextProvider.getContext()).getRegistry().replace(GlideUrl.class, InputStream.class, new OkHttpUrlLoader.Factory(builder.build()));
    }

    public static void initRequestCommonParams() {
        OkHttpClient.Builder newBuilder = OkHttpClientProvider.okHttpClient().newBuilder();
        newBuilder.connectTimeout((long) DEFAULT_TIME_OUT, TimeUnit.SECONDS).cookieJar(new CookieJar() { // from class: com.che168.autotradercloud.launch.model.LaunchModel.3
            public void saveFromResponse(HttpUrl httpUrl, List<Cookie> list) {
                ATCCookiesManager.INSTANCE.setRequestCookie(list);
            }

            public List<Cookie> loadForRequest(HttpUrl httpUrl) {
                return ATCCookiesManager.INSTANCE.getCookieListByHost(httpUrl.toString());
            }
        });
        new HttpUtil.ConfigBuilder().baseUrl(HostHelp.HOST_DEALERCLOUD_API).client(newBuilder.build()).paramsInterceptor(new ParamsInterceptor() { // from class: com.che168.autotradercloud.launch.model.LaunchModel$$ExternalSyntheticLambda0
            public final TreeMap checkParams(int i, TreeMap treeMap) {
                return LaunchModel.lambda$initRequestCommonParams$0(i, treeMap);
            }
        }).headersInterceptor(new HeadersInterceptor() { // from class: com.che168.autotradercloud.launch.model.LaunchModel$$ExternalSyntheticLambda1
            public final Map checkHeader(Map map) {
                return LaunchModel.lambda$initRequestCommonParams$1(map);
            }
        }).networkStatisticsInterceptor(new NetworkStatisticsUtil()).hostInterceptor(new HostInterceptor() { // from class: com.che168.autotradercloud.launch.model.LaunchModel$$ExternalSyntheticLambda2
            public final boolean hostNameVerifier(String str) {
                return LaunchModel.lambda$initRequestCommonParams$2(str);
            }
        }).build();
    }

    /* JADX INFO: Access modifiers changed from: package-private */
    public static /* synthetic */ TreeMap lambda$initRequestCommonParams$0(int i, TreeMap treeMap) {
        if (!treeMap.containsKey(KEY_APP_ID)) {
            treeMap.put(KEY_APP_ID, Constants.APP_ID);
        }
        if (!treeMap.containsKey(KEY_CHANNEL_ID)) {
            treeMap.put(KEY_CHANNEL_ID, AppUtils.getChannelId(ContextProvider.getContext()));
        }
        if (!treeMap.containsKey(KEY_APP_VERSION)) {
            treeMap.put(KEY_APP_VERSION, SystemUtil.getAppVersionName(ContextProvider.getContext()));
        }
        if (!treeMap.containsKey(KEY_UDID)) {
            treeMap.put(KEY_UDID, AppUtils.getUDID(ContextProvider.getContext()));
        }
        String userKey = UserModel.getUserKey();
        if (!ATCEmptyUtil.isEmpty(userKey)) {
            treeMap.put(KEY_USERKEY, userKey);
        }
        checkNullParams(treeMap);
        String signByType = SignManager.INSTANCE.signByType(i, treeMap);
        if (signByType != null) {
            treeMap.put(KEY_SIGN, signByType);
        }
        return treeMap;
    }

    /* JADX INFO: Access modifiers changed from: package-private */
    public static /* synthetic */ Map lambda$initRequestCommonParams$1(Map map) {
        map.put("Cache-Control", "public, max-age=0");
        map.put("traceid", "atc.android_" + UUID.randomUUID().toString());
        return map;
    }

    /* JADX INFO: Access modifiers changed from: package-private */
    public static /* synthetic */ boolean lambda$initRequestCommonParams$2(String str) {
        for (String str2 : HOST_WHITE_LIST) {
            if (str.endsWith(str2)) {
                return true;
            }
        }
        return false;
    }

    private static void checkNullParams(Map<String, String> map) {
        for (String str : map.keySet()) {
            if (map.get(str) == null) {
                map.put(str, "");
            }
        }
    }

    /* JADX WARN: Type inference failed for: r2v3, types: [com.che168.autotradercloud.launch.model.LaunchModel$4] */
    public static void getAppImage(String str, int i, ResponseCallback<AppImageBean> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(GET_APP_IMAGE).param("type", String.valueOf(i));
        doRequest(builder, responseCallback, new TypeToken<BaseResult<AppImageBean>>() { // from class: com.che168.autotradercloud.launch.model.LaunchModel.4
        }.getType());
    }

    public static TreeMap<String, String> getRequestParams(TreeMap<String, String> treeMap) {
        if (!treeMap.containsKey(KEY_APP_ID)) {
            treeMap.put(KEY_APP_ID, Constants.APP_ID);
        }
        if (!treeMap.containsKey(KEY_CHANNEL_ID)) {
            treeMap.put(KEY_CHANNEL_ID, AppUtils.getChannelId(ContextProvider.getContext()));
        }
        if (!treeMap.containsKey(KEY_APP_VERSION)) {
            treeMap.put(KEY_APP_VERSION, SystemUtil.getAppVersionName(ContextProvider.getContext()));
        }
        if (!treeMap.containsKey(KEY_UDID)) {
            treeMap.put(KEY_UDID, AppUtils.getUDID(ContextProvider.getContext()));
        }
        String userKey = UserModel.getUserKey();
        if (!ATCEmptyUtil.isEmpty(userKey)) {
            treeMap.put(KEY_USERKEY, userKey);
        }
        checkNullParams(treeMap);
        treeMap.put(KEY_SIGN, SignManager.INSTANCE.signByType(0, treeMap));
        return treeMap;
    }

    /* JADX WARN: Type inference failed for: r2v1, types: [com.che168.autotradercloud.launch.model.LaunchModel$6] */
    public static void loadOnlineParams(final ILoadOnlineParamsCallback iLoadOnlineParamsCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.url(GET_ONLINE_PARAMS);
        doRequest(builder, new ResponseCallback<JsonArray>() { // from class: com.che168.autotradercloud.launch.model.LaunchModel.5
            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void success(JsonArray jsonArray) {
                if (jsonArray != null && jsonArray.size() > 0) {
                    HashMap hashMap = new HashMap();
                    Iterator it = jsonArray.iterator();
                    while (it.hasNext()) {
                        JsonObject asJsonObject = ((JsonElement) it.next()).getAsJsonObject();
                        hashMap.put(asJsonObject.get("Key").getAsString(), asJsonObject.get("Value").getAsString());
                    }
                    LaunchModel.mOnlineParams = hashMap;
                    SPUtils.save(LaunchModel.KEY_ONLINE_PARAMS, GsonUtil.toJson(hashMap));
                    ILoadOnlineParamsCallback iLoadOnlineParamsCallback2 = ILoadOnlineParamsCallback.this;
                    if (iLoadOnlineParamsCallback2 != null) {
                        iLoadOnlineParamsCallback2.callback(hashMap);
                        return;
                    }
                    return;
                }
                SPUtils.remove(LaunchModel.KEY_ONLINE_PARAMS);
                ILoadOnlineParamsCallback iLoadOnlineParamsCallback3 = ILoadOnlineParamsCallback.this;
                if (iLoadOnlineParamsCallback3 != null) {
                    iLoadOnlineParamsCallback3.callback(null);
                }
            }

            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void failed(int i, ApiException apiException) {
                ILoadOnlineParamsCallback iLoadOnlineParamsCallback2 = ILoadOnlineParamsCallback.this;
                if (iLoadOnlineParamsCallback2 != null) {
                    iLoadOnlineParamsCallback2.callback(null);
                }
            }
        }, new TypeToken<BaseResult<JsonArray>>() { // from class: com.che168.autotradercloud.launch.model.LaunchModel.6
        }.getType());
    }

    /* JADX WARN: Type inference failed for: r1v1, types: [com.che168.autotradercloud.launch.model.LaunchModel$7] */
    private static Map<String, String> getOnlineParams() {
        Map<String, String> map = mOnlineParams;
        if (map == null || map.isEmpty()) {
            String str = SPUtils.get(KEY_ONLINE_PARAMS);
            if (!ATCEmptyUtil.isEmpty(str)) {
                mOnlineParams = (Map) GsonUtil.fromJson(str, new TypeToken<HashMap<String, String>>() { // from class: com.che168.autotradercloud.launch.model.LaunchModel.7
                }.getType());
            }
        }
        return mOnlineParams;
    }

    public static String getOnlineParam(String str) {
        Map<String, String> onlineParams = getOnlineParams();
        return onlineParams != null ? onlineParams.get(str) : "";
    }

    public static boolean isOnlineParamChange(String str, String str2) {
        if (ATCEmptyUtil.isEmpty(str)) {
            return false;
        }
        String onlineParam = getOnlineParam(str);
        if (SPUtils.get(str, str2).equals(onlineParam)) {
            return false;
        }
        SPUtils.save(str, onlineParam);
        return true;
    }
}
