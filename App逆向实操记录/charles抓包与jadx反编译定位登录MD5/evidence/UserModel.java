package com.che168.autotradercloud.user.model;

import android.content.Context;
import android.content.Intent;
import android.database.sqlite.SQLiteDatabase;
import android.text.TextUtils;
import android.view.View;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import com.autohome.ahkit.utils.SecurityUtil;
import com.che168.ahnetwork.http.HttpUtil;
import com.che168.atcimkit.ATCIMKitManager;
import com.che168.atclibrary.base.AppManager;
import com.che168.atclibrary.db.AssetsDatabaseManager;
import com.che168.atclibrary.file.FilePathUtil;
import com.che168.atclibrary.file.FileRootType;
import com.che168.atclibrary.provider.ContextProvider;
import com.che168.atclibrary.utils.ATCEmptyUtil;
import com.che168.atclibrary.utils.FileUtil;
import com.che168.atclibrary.utils.GsonUtil;
import com.che168.atclibrary.utils.LogUtil;
import com.che168.atclibrary.utils.SystemUtil;
import com.che168.autotradercloud.base.TtpManager;
import com.che168.autotradercloud.base.httpNew.ApiException;
import com.che168.autotradercloud.base.httpNew.BaseModel;
import com.che168.autotradercloud.base.httpNew.BaseResult;
import com.che168.autotradercloud.base.httpNew.ResponseCallback;
import com.che168.autotradercloud.base.js.bean.JSUrl;
import com.che168.autotradercloud.jump.JumpPageController;
import com.che168.autotradercloud.market.bean.CZYDealerBean;
import com.che168.autotradercloud.market.model.StoreActivityModelKt;
import com.che168.autotradercloud.my.PasswordModifyActivity;
import com.che168.autotradercloud.my.bean.WelfaredesBean;
import com.che168.autotradercloud.my.db.EmployeeTable;
import com.che168.autotradercloud.permissions.UserPermissionsManage;
import com.che168.autotradercloud.purchase_manage.model.PurchaseModel;
import com.che168.autotradercloud.statistics.BaseAnalytics;
import com.che168.autotradercloud.user.bean.CZYDealerCacheInfoBean;
import com.che168.autotradercloud.user.bean.CplStatusBean;
import com.che168.autotradercloud.user.bean.DealerDiscountsInfo;
import com.che168.autotradercloud.user.bean.DealerSectionInfoBean;
import com.che168.autotradercloud.user.bean.DealerWeChatInfo;
import com.che168.autotradercloud.user.bean.GoldStoreBean;
import com.che168.autotradercloud.user.bean.GuideConfigBean;
import com.che168.autotradercloud.user.bean.UserBean;
import com.che168.autotradercloud.user.bean.UserMemberHeadBean;
import com.che168.autotradercloud.user.bean.UserPermissionsBean;
import com.che168.autotradercloud.user.db.UserPermissionsDbHelp;
import com.che168.autotradercloud.util.DesUtils;
import com.che168.autotradercloud.util.HostHelp;
import com.che168.autotradercloud.util.ImageManager;
import com.che168.autotradercloud.util.SPUtils;
import com.che168.autotradercloud.util.UserConfigUtil;
import com.che168.autotradercloud.wallet.bean.MemberRightType;
import com.che168.autotradercloud.widget.dialog.DialogUtils;
import com.che168.selectcity.bean.SelectCityBean;
import com.google.gson.JsonObject;
import com.google.gson.reflect.TypeToken;
import com.ttp.module_common.common.Const;
import io.reactivex.Single;
import io.reactivex.SingleEmitter;
import io.reactivex.SingleOnSubscribe;
import io.reactivex.SingleSource;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.functions.Consumer;
import io.reactivex.functions.Function;
import io.reactivex.schedulers.Schedulers;
import io.reactivex.subjects.SingleSubject;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeMap;
/* loaded from: classes3.dex */
public class UserModel extends BaseModel {
    public static final String ACTION_DEALER_CACHE_INFO_CHANGE = "action_dealer_cache_info_change";
    private static final String CHECK_CODE = "/tradercloud/v101/login/checkcode.ashx";
    private static final String CZY_DEALER_INFO_URL = "/tradercloud/v1995/dealer/getdealerdetailinfo.ashx";
    private static final String GET_DEALER_DICOUNTS_INFO = "/tradercloud/v190/dealer/GetDealerDisInfo.ashx";
    private static final String GET_DEALER_INFO = "/tradercloud/v199/dealersection/getdealersectioninfo.ashx";
    private static final String KEY_DEALER_SECTION_INFO = "KEY_DEALER_SECTION_INFO";
    public static final String KEY_DEALER_WE_CHAT_CODE = "key_dealer_we_chat_code";
    public static final String LOGIN_URL = "/tradercloud/sealed/login/login.ashx";
    private static final String LOGOUT_URL = "/tradercloud/v100/login/logout.ashx";
    private static final String RESET_PWD = "/tradercloud/v101/login/resetpwdforapp.ashx";
    private static final String SEND_CODE_FIND_PWD = "/tradercloud/v101/login/sendcodeforfindpwd.ashx";
    public static final String TAG_DEALER_CACHE_INFO = "tag_dealer_cache_info";
    private static UserBean mUserBean;
    private static final String PERMISSIONS_SYNC_URL = HostHelp.HOST_APICZY + "/private/tradercloud/v100/common/GetMemberAuth.ashx";
    private static final String CZY_DEALER_CACHE_INFO_URL = HostHelp.HOST_APICZY + "/private/static/cacheinfo";
    private static final String GET_CPL_DEALER_INFO = HostHelp.HOST_APICZY + "/private/tradercloud/v199/cpl/GetCPL_DealersInfo.ashx";
    private static final String GET_SHOP_BASE_INFO = HostHelp.HOST_APPS_API + "/phone/v54/shop/GetShopBaseInfo.ashx";
    private static final String UPDATE_USER_INFO = HostHelp.HOST_APICZY + "/protected/v1912/dealer/checklogin";
    private static final String GET_CPL_ARREARS = HostHelp.HOST_DEALERCLOUD_API + "/tradercloud/v199/cpl/GetCPL_ArrearsInfoByDealerID.ashx ";
    private static String UPFileName = "userPermissions.txt";
    private static Set<Integer> userPermissions = null;
    private static final String POST_CITY_INFO = HostHelp.HOST_APIDEALER + "/private/login/cityinfo";
    private static final String GET_MEMBER_PHOTO = HostHelp.HOST_APIDEALER + "/private/minp/memberhead";
    private static final String GET_CLUB_CERTIFICATION = HostHelp.HOST_SAAS_BUSSINESS_API + "/dealer/v100-pd/dealer/club/certification/isexist";
    private static final String GET_DEALER_SALE_WE_CHAT = HostHelp.HOST_APIDEALER + "/private/dealer/dealerssale/getinfo";
    private static final String POST_DEALER_SALE_WE_CHAT = HostHelp.HOST_APIDEALER + "/private/dealer/dealerssale/updatewx";
    private static final String EDIT_MEMBER_INFO = HostHelp.HOST_APIDEALER + "/private/minp/editmember";
    private static final String GET_WELFAREDES = HostHelp.HOST_APIDEALER + "/private/productgroup/welfaredes";
    private static final String LOGIN_BY_MOBILE = HostHelp.HOST_DEALERCLOUD_API + "/tradercloud/sealed/login/loginbymobile.ashx";

    public static boolean isMemberProdudtTypes(int i) {
        return false;
    }

    public static void reportUserLocation(final String str, final String str2, final String str3, final String str4) {
        new Thread(new Runnable() { // from class: com.che168.autotradercloud.user.model.UserModel.1
            @Override // java.lang.Runnable
            public void run() {
                HttpUtil.Builder builder = new HttpUtil.Builder();
                builder.tag(str).url(UserModel.POST_CITY_INFO).method(HttpUtil.Method.POST).param("ip", SystemUtil.GetNetIp()).param("maplon", str2).param("maplat", str3).param(Const.ADDRESS_STR, str4);
                BaseModel.doRequest(builder, null, new TypeToken<BaseResult<Object>>() { // from class: com.che168.autotradercloud.user.model.UserModel.1.1
                }.getType());
            }
        }).start();
    }

    public static void getAuthCode(String str, String str2, ResponseCallback<Object> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(SEND_CODE_FIND_PWD).method(HttpUtil.Method.POST).param(EmployeeTable.C_MOBILE, str2);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<Object>>() { // from class: com.che168.autotradercloud.user.model.UserModel.2
        }.getType());
    }

    public static void checkAuthCode(String str, String str2, String str3, ResponseCallback<Object> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(CHECK_CODE).method(HttpUtil.Method.POST).param("code", str3).param(EmployeeTable.C_MOBILE, str2);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<Object>>() { // from class: com.che168.autotradercloud.user.model.UserModel.3
        }.getType());
    }

    public static void resetPwd(String str, String str2, String str3, String str4, ResponseCallback<Object> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(RESET_PWD).method(HttpUtil.Method.POST).param("pwd", str4).param("code", str3).param(EmployeeTable.C_MOBILE, str2);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<Object>>() { // from class: com.che168.autotradercloud.user.model.UserModel.4
        }.getType());
    }

    public static void loginByPassword(String str, String str2, String str3, String str4, String str5, ResponseCallback<UserBean> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).method(HttpUtil.Method.POST).signType(1).url(LOGIN_URL).param("username", str2).param("type", str4).param("signkey", str5).param("pwd", SecurityUtil.encodeMD5(str3));
        doRequest(builder, responseCallback, new TypeToken<BaseResult<UserBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.5
        }.getType());
    }

    public static void logout(String str, ResponseCallback<Object> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).method(HttpUtil.Method.POST).url(LOGOUT_URL);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<Object>>() { // from class: com.che168.autotradercloud.user.model.UserModel.6
        }.getType());
    }

    public static void getGoldShopBaseInfo(String str, long j, ResponseCallback<GoldStoreBean> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(GET_SHOP_BASE_INFO).param("dealerid", String.valueOf(j));
        doRequest(builder, responseCallback, new TypeToken<BaseResult<GoldStoreBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.7
        }.getType());
    }

    public static void updateUserInfo(ResponseCallback<UserBean> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.method(HttpUtil.Method.POST).url(UPDATE_USER_INFO);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<UserBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.8
        }.getType());
    }

    public static void saveDealerInfo(String str) {
        SPUtils.saveCYZDealerInfo(str);
        CZYDealerBean cZYDealerBean = (CZYDealerBean) GsonUtil.fromJson(str, new TypeToken<CZYDealerBean>() { // from class: com.che168.autotradercloud.user.model.UserModel.9
        }.getType());
    }

    public static void saveDealerInfo(CZYDealerBean cZYDealerBean) {
        SPUtils.saveCYZDealerInfo(GsonUtil.toJson(cZYDealerBean));
    }

    public static CZYDealerBean getDealerInfo() {
        CZYDealerBean cZYDealerInfo = SPUtils.getCZYDealerInfo();
        if (cZYDealerInfo == null) {
            AppManager.getInstance().finishAll();
            JumpPageController.goLoginPage(ContextProvider.getContext());
            return new CZYDealerBean();
        }
        return cZYDealerInfo;
    }

    public static CZYDealerCacheInfoBean getDealerCacheInfo() {
        CZYDealerCacheInfoBean cZYDealerCacheInfo = SPUtils.getCZYDealerCacheInfo();
        if (cZYDealerCacheInfo == null) {
            AppManager.getInstance().finishAll();
            JumpPageController.goLoginPage(ContextProvider.getContext());
            return new CZYDealerCacheInfoBean();
        }
        return cZYDealerCacheInfo;
    }

    public static void clearDealerInfo() {
        SPUtils.clearDealerInfo();
        SPUtils.clearDealerCacheInfo();
        StoreActivityModelKt.INSTANCE.setWhite(false);
    }

    /* JADX INFO: Access modifiers changed from: private */
    public static void getCZYDealerInfo(ResponseCallback<JsonObject> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.method(HttpUtil.Method.GET).url(CZY_DEALER_INFO_URL);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<JsonObject>>() { // from class: com.che168.autotradercloud.user.model.UserModel.10
        }.getType());
    }

    /* JADX INFO: Access modifiers changed from: private */
    public static void getCZYDealerCacheInfo(ResponseCallback<JsonObject> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.method(HttpUtil.Method.GET).url(CZY_DEALER_CACHE_INFO_URL);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<JsonObject>>() { // from class: com.che168.autotradercloud.user.model.UserModel.11
        }.getType());
    }

    public static void loadDealerInfo() {
        loadBaseDealerInfo().flatMap(new Function<CZYDealerBean, SingleSource<CZYDealerCacheInfoBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.14
            @Override // io.reactivex.functions.Function
            public SingleSource<CZYDealerCacheInfoBean> apply(CZYDealerBean cZYDealerBean) {
                return UserModel.loadDealerCacheInfo();
            }
        }).subscribeOn(Schedulers.io()).observeOn(AndroidSchedulers.mainThread()).subscribe(new Consumer<CZYDealerCacheInfoBean>() { // from class: com.che168.autotradercloud.user.model.UserModel.12
            @Override // io.reactivex.functions.Consumer
            public void accept(CZYDealerCacheInfoBean cZYDealerCacheInfoBean) {
            }
        }, new Consumer<Throwable>() { // from class: com.che168.autotradercloud.user.model.UserModel.13
            @Override // io.reactivex.functions.Consumer
            public void accept(Throwable th) throws Exception {
            }
        });
    }

    public static Single<CZYDealerBean> loadBaseDealerInfo() {
        return SingleSubject.create(new SingleOnSubscribe<CZYDealerBean>() { // from class: com.che168.autotradercloud.user.model.UserModel.15
            @Override // io.reactivex.SingleOnSubscribe
            public void subscribe(final SingleEmitter<CZYDealerBean> singleEmitter) throws Exception {
                if (!UserModel.isLogin()) {
                    singleEmitter.onError(new ApiException("用户未登录"));
                } else {
                    UserModel.getCZYDealerInfo(new ResponseCallback<JsonObject>() { // from class: com.che168.autotradercloud.user.model.UserModel.15.1
                        @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
                        public void success(JsonObject jsonObject) {
                            if (!ATCEmptyUtil.isEmpty(jsonObject)) {
                                String jsonObject2 = jsonObject.toString();
                                UserModel.saveDealerInfo(jsonObject2);
                                singleEmitter.onSuccess((CZYDealerBean) GsonUtil.fromJson(jsonObject2, new TypeToken<CZYDealerBean>() { // from class: com.che168.autotradercloud.user.model.UserModel.15.1.1
                                }.getType()));
                                return;
                            }
                            singleEmitter.onError(new ApiException("商家信息为空"));
                        }

                        @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
                        public void failed(int i, ApiException apiException) {
                            LogUtil.e(apiException.toString());
                            singleEmitter.onError(apiException);
                        }
                    });
                }
            }
        });
    }

    public static Single<CZYDealerCacheInfoBean> loadDealerCacheInfo() {
        return SingleSubject.create(new SingleOnSubscribe<CZYDealerCacheInfoBean>() { // from class: com.che168.autotradercloud.user.model.UserModel.16
            @Override // io.reactivex.SingleOnSubscribe
            public void subscribe(final SingleEmitter<CZYDealerCacheInfoBean> singleEmitter) throws Exception {
                if (!UserModel.isLogin()) {
                    singleEmitter.onError(new ApiException("用户未登录"));
                } else {
                    UserModel.getCZYDealerCacheInfo(new ResponseCallback<JsonObject>() { // from class: com.che168.autotradercloud.user.model.UserModel.16.1
                        @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
                        public void success(JsonObject jsonObject) {
                            if (!ATCEmptyUtil.isEmpty(jsonObject)) {
                                String jsonObject2 = jsonObject.toString();
                                String cZYDealerCacheInfoStr = SPUtils.getCZYDealerCacheInfoStr();
                                CZYDealerCacheInfoBean cZYDealerCacheInfoBean = (CZYDealerCacheInfoBean) GsonUtil.fromJson(jsonObject2, new TypeToken<CZYDealerCacheInfoBean>() { // from class: com.che168.autotradercloud.user.model.UserModel.16.1.1
                                }.getType());
                                SPUtils.saveCYZDealerCacheInfo(jsonObject2);
                                if (jsonObject2 != null && !jsonObject2.equals(cZYDealerCacheInfoStr)) {
                                    LogUtil.d(UserModel.TAG_DEALER_CACHE_INFO, "DealerCacheInfo刷新了");
                                    LocalBroadcastManager.getInstance(ContextProvider.getContext()).sendBroadcast(new Intent(UserModel.ACTION_DEALER_CACHE_INFO_CHANGE));
                                }
                                singleEmitter.onSuccess(cZYDealerCacheInfoBean);
                                return;
                            }
                            singleEmitter.onError(new ApiException("商家配置信息为空"));
                        }

                        @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
                        public void failed(int i, ApiException apiException) {
                            LogUtil.e(apiException.toString());
                            singleEmitter.onError(apiException);
                        }
                    });
                }
            }
        });
    }

    public static Single<String> loadDealerCacheInfoForH5() {
        return SingleSubject.create(new SingleOnSubscribe() { // from class: com.che168.autotradercloud.user.model.UserModel$$ExternalSyntheticLambda0
            @Override // io.reactivex.SingleOnSubscribe
            public final void subscribe(SingleEmitter singleEmitter) {
                UserModel.lambda$loadDealerCacheInfoForH5$0(singleEmitter);
            }
        });
    }

    /* JADX INFO: Access modifiers changed from: package-private */
    public static /* synthetic */ void lambda$loadDealerCacheInfoForH5$0(final SingleEmitter singleEmitter) throws Exception {
        if (!isLogin()) {
            singleEmitter.onError(new ApiException("用户未登录"));
        } else {
            getCZYDealerCacheInfo(new ResponseCallback<JsonObject>() { // from class: com.che168.autotradercloud.user.model.UserModel.17
                @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
                public void success(JsonObject jsonObject) {
                    if (!ATCEmptyUtil.isEmpty(jsonObject)) {
                        String jsonObject2 = jsonObject.toString();
                        SPUtils.saveCYZDealerCacheInfo(jsonObject2);
                        SingleEmitter.this.onSuccess(jsonObject2);
                        return;
                    }
                    SingleEmitter.this.onError(new ApiException("商家配置信息为空"));
                }

                @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
                public void failed(int i, ApiException apiException) {
                    LogUtil.e(apiException.toString());
                    SingleEmitter.this.onError(apiException);
                }
            });
        }
    }

    public static void saveUserInfo(UserBean userBean) {
        if (userBean != null) {
            SPUtils.saveUserInfo(userBean);
            mUserBean = null;
            if (userBean.isLogin()) {
                return;
            }
            SPUtils.saveIsLogin(false);
        }
    }

    public static UserBean getUserInfo() {
        if (mUserBean == null) {
            UserBean userInfo = SPUtils.getUserInfo();
            mUserBean = userInfo;
            if (userInfo == null) {
                mUserBean = new UserBean();
            }
        }
        return mUserBean;
    }

    public static void clearLocalLoginInfo() {
        clearUserPermissionCodes();
        clearCacheUserPermission();
        mUserBean = null;
        SPUtils.clearUserInfo();
        clearDealerInfo();
        SystemUtil.clearCookies(ContextProvider.getContext());
        SPUtils.clearAppGrayRelease();
        PurchaseModel.clearHotSeries();
        BaseAnalytics.resetCommonEventParams();
        AssetsDatabaseManager.closeAllDatabase();
        ATCIMKitManager.Companion.getInstance().logout(ContextProvider.getContext());
        TtpManager.INSTANCE.logout();
    }

    public static void getCPLDealerInfo(String str, ResponseCallback<CplStatusBean> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(GET_CPL_DEALER_INFO);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<CplStatusBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.18
        }.getType());
    }

    public static void loadCPLDealerInfo() {
        loadCPLDealerInfo(null, null);
    }

    public static void loadCPLDealerInfo(String str, final ResponseCallback<CplStatusBean> responseCallback) {
        getCPLDealerInfo(str, new ResponseCallback<CplStatusBean>() { // from class: com.che168.autotradercloud.user.model.UserModel.19
            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void success(CplStatusBean cplStatusBean) {
                if (cplStatusBean != null) {
                    UserConfigUtil.saveCPLDealerInfo(cplStatusBean);
                    ResponseCallback responseCallback2 = ResponseCallback.this;
                    if (responseCallback2 != null) {
                        responseCallback2.success(cplStatusBean);
                    }
                }
                ResponseCallback responseCallback3 = ResponseCallback.this;
                if (responseCallback3 != null) {
                    responseCallback3.failed(-2, null);
                }
            }

            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void failed(int i, ApiException apiException) {
                LogUtil.e(apiException.toString());
                ResponseCallback responseCallback2 = ResponseCallback.this;
                if (responseCallback2 != null) {
                    responseCallback2.failed(i, apiException);
                }
            }
        });
    }

    public static boolean isNewCPLDealer() {
        CplStatusBean cplDealerStatus = getCplDealerStatus();
        return cplDealerStatus != null && cplDealerStatus.status == 10;
    }

    public static boolean isCPLDealer() {
        CplStatusBean cplDealerStatus = getCplDealerStatus();
        return (cplDealerStatus == null || cplDealerStatus.status == 0 || cplDealerStatus.status == 10) ? false : true;
    }

    public static boolean isPulishCarDealer() {
        CplStatusBean cplDealerStatus = getCplDealerStatus();
        return cplDealerStatus != null && cplDealerStatus.publiccarstatus == 1;
    }

    public static CplStatusBean getCplDealerStatus() {
        CplStatusBean cPLDealerInfo = UserConfigUtil.getCPLDealerInfo();
        if (cPLDealerInfo == null) {
            cPLDealerInfo = new CplStatusBean();
            if (getDealerInfo() != null) {
                cPLDealerInfo.status = getDealerInfo().getCPLStatus();
            }
            UserConfigUtil.saveCPLDealerInfo(cPLDealerInfo);
            loadCPLDealerInfo();
        }
        return cPLDealerInfo;
    }

    public static boolean isLogin() {
        return (getUserInfo() == null || ATCEmptyUtil.isEmpty((CharSequence) getUserInfo().userkey)) ? false : true;
    }

    public static boolean isAdmin() {
        UserBean userInfo = getUserInfo();
        return userInfo != null && userInfo.isadmin == 1;
    }

    public static boolean isFistOpen() {
        UserBean userInfo = getUserInfo();
        if (userInfo != null) {
            return userInfo.isFirstOpen();
        }
        return false;
    }

    public static boolean isMcbOpen() {
        CZYDealerBean dealerInfo = getDealerInfo();
        if (dealerInfo == null) {
            return false;
        }
        return dealerInfo.isMcbOpen();
    }

    public static String getUserKey() {
        UserBean userInfo = SPUtils.getUserInfo();
        if (userInfo != null) {
            return userInfo.userkey;
        }
        return null;
    }

    public static String getCacheLoginTime() {
        UserBean userInfo = SPUtils.getUserInfo();
        if (userInfo != null) {
            return userInfo.currenttime;
        }
        return null;
    }

    public static void createUserFile(String str) {
        String encodeMD5 = SecurityUtil.encodeMD5(str);
        if (ATCEmptyUtil.isEmpty((CharSequence) encodeMD5)) {
            LogUtil.e("create user error!");
            return;
        }
        try {
            File file = new File(FilePathUtil.getRootDataFilePath(), encodeMD5);
            if (file.exists()) {
                return;
            }
            file.mkdirs();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static File getUserFile() {
        if (!isLogin()) {
            LogUtil.e("create user file error!");
            return null;
        }
        String encodeMD5 = SecurityUtil.encodeMD5(getUserInfo().memberid);
        if (encodeMD5 == null) {
            return null;
        }
        File file = new File(FilePathUtil.getRootDataPath(), encodeMD5);
        File file2 = new File(FilePathUtil.getRootDataFilePath(), encodeMD5);
        if (file.exists()) {
            FileUtil.copyDir(file.getAbsolutePath(), file2.getAbsolutePath());
            FileUtil.deleteFiles(file);
        }
        if (!file2.exists()) {
            file2.mkdirs();
        }
        return file2;
    }

    public static File getUserConfigFile() {
        File userFile = getUserFile();
        if (userFile != null) {
            File file = new File(userFile, "userConfig.properties");
            if (file.exists()) {
                return file;
            }
            try {
                file.createNewFile();
                return file;
            } catch (IOException e) {
                e.printStackTrace();
                return file;
            }
        }
        return null;
    }

    public static void clearUserUploadTmpFile() {
        File userFile = getUserFile();
        if (userFile != null) {
            FileUtil.delete(new File(userFile, ImageManager.UPLOAD_PIC_TMP));
            FileUtil.delete(new File(FilePathUtil.getFilePath(FileRootType.SD_ROOT_APP, "image")));
        }
    }

    public static void userPermissionsSync(final ResponseCallback<List<UserPermissionsBean>> responseCallback, final UserPermissionsManage.UserPermissionsChangeInterface userPermissionsChangeInterface) {
        if (getUserInfo() == null) {
            return;
        }
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.url(PERMISSIONS_SYNC_URL);
        builder.param(EmployeeTable.C_ISADMIN, getUserInfo().isadmin + "");
        doRequest(builder, new ResponseCallback<List<UserPermissionsBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.20
            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void success(List<UserPermissionsBean> list) {
                ResponseCallback responseCallback2 = ResponseCallback.this;
                if (responseCallback2 != null) {
                    responseCallback2.success(list);
                }
                UserModel.updatePermissions(list, userPermissionsChangeInterface);
            }

            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void failed(int i, ApiException apiException) {
                ResponseCallback responseCallback2 = ResponseCallback.this;
                if (responseCallback2 != null) {
                    responseCallback2.failed(i, apiException);
                }
            }
        }, new TypeToken<BaseResult<List<UserPermissionsBean>>>() { // from class: com.che168.autotradercloud.user.model.UserModel.21
        }.getType());
    }

    /* JADX INFO: Access modifiers changed from: private */
    /* JADX WARN: Code restructure failed: missing block: B:32:0x0095, code lost:
        if (r4 != null) goto L40;
     */
    /* JADX WARN: Code restructure failed: missing block: B:33:0x0097, code lost:
        r4.close();
     */
    /* JADX WARN: Code restructure failed: missing block: B:39:0x00a1, code lost:
        if (r4 == null) goto L44;
     */
    /* JADX WARN: Removed duplicated region for block: B:53:0x00fb A[Catch: all -> 0x0107, TryCatch #1 {, blocks: (B:9:0x000d, B:11:0x000f, B:13:0x0018, B:14:0x0023, B:16:0x002a, B:18:0x0032, B:20:0x004a, B:21:0x004f, B:22:0x0052, B:24:0x005c, B:33:0x0097, B:44:0x00aa, B:46:0x00b6, B:53:0x00fb, B:54:0x0100, B:55:0x0103, B:48:0x00cb, B:50:0x00dc, B:51:0x00f0, B:57:0x0105, B:26:0x0077, B:28:0x007d, B:30:0x0083, B:38:0x009e), top: B:62:0x000b }] */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    public static boolean updatePermissions(java.util.List<com.che168.autotradercloud.user.bean.UserPermissionsBean> r9, com.che168.autotradercloud.permissions.UserPermissionsManage.UserPermissionsChangeInterface r10) {
        /*
            Method dump skipped, instructions count: 266
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.che168.autotradercloud.user.model.UserModel.updatePermissions(java.util.List, com.che168.autotradercloud.permissions.UserPermissionsManage$UserPermissionsChangeInterface):boolean");
    }

    public static synchronized Set<Integer> getUserPermissionCodes() {
        Set<Integer> set;
        synchronized (UserModel.class) {
            if (userPermissions == null) {
                userPermissions = new HashSet();
                updatePermissions(getUserPermissions(), null);
            }
            set = userPermissions;
        }
        return set;
    }

    public static synchronized void clearUserPermissionCodes() {
        synchronized (UserModel.class) {
            Set<Integer> set = userPermissions;
            if (set != null) {
                set.clear();
            }
        }
    }

    public static synchronized void clearCacheUserPermission() {
        synchronized (UserModel.class) {
            File uPFile = getUPFile();
            if (uPFile != null && uPFile.exists()) {
                uPFile.delete();
            }
        }
    }

    /* JADX WARN: Code restructure failed: missing block: B:35:0x0044, code lost:
        if (r1 == null) goto L61;
     */
    /* JADX WARN: Removed duplicated region for block: B:57:0x0051 A[EXC_TOP_SPLITTER, SYNTHETIC] */
    /* JADX WARN: Removed duplicated region for block: B:59:0x004a A[EXC_TOP_SPLITTER, SYNTHETIC] */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    private static synchronized void saveUserPermissions(java.util.List<com.che168.autotradercloud.user.bean.UserPermissionsBean> r4) {
        /*
            java.lang.Class<com.che168.autotradercloud.user.model.UserModel> r0 = com.che168.autotradercloud.user.model.UserModel.class
            monitor-enter(r0)
            if (r4 != 0) goto L7
            monitor-exit(r0)
            return
        L7:
            java.lang.String r4 = com.che168.atclibrary.utils.GsonUtil.toJson(r4)     // Catch: java.lang.Throwable -> L57
            java.io.File r1 = getUPFile()     // Catch: java.lang.Throwable -> L57
            if (r1 == 0) goto L55
            r2 = 0
            java.io.FileWriter r3 = new java.io.FileWriter     // Catch: java.lang.Throwable -> L35 java.io.IOException -> L38
            r3.<init>(r1)     // Catch: java.lang.Throwable -> L35 java.io.IOException -> L38
            java.io.BufferedWriter r1 = new java.io.BufferedWriter     // Catch: java.lang.Throwable -> L2d java.io.IOException -> L31
            r1.<init>(r3)     // Catch: java.lang.Throwable -> L2d java.io.IOException -> L31
            r1.write(r4)     // Catch: java.lang.Throwable -> L29 java.io.IOException -> L2b
            r1.flush()     // Catch: java.lang.Throwable -> L29 java.io.IOException -> L2b
            r3.close()     // Catch: java.io.IOException -> L25 java.lang.Throwable -> L57
        L25:
            r1.close()     // Catch: java.io.IOException -> L55 java.lang.Throwable -> L57
            goto L55
        L29:
            r4 = move-exception
            goto L2f
        L2b:
            r4 = move-exception
            goto L33
        L2d:
            r4 = move-exception
            r1 = r2
        L2f:
            r2 = r3
            goto L48
        L31:
            r4 = move-exception
            r1 = r2
        L33:
            r2 = r3
            goto L3a
        L35:
            r4 = move-exception
            r1 = r2
            goto L48
        L38:
            r4 = move-exception
            r1 = r2
        L3a:
            r4.printStackTrace()     // Catch: java.lang.Throwable -> L47
            if (r2 == 0) goto L44
            r2.close()     // Catch: java.io.IOException -> L43 java.lang.Throwable -> L57
            goto L44
        L43:
        L44:
            if (r1 == 0) goto L55
            goto L25
        L47:
            r4 = move-exception
        L48:
            if (r2 == 0) goto L4f
            r2.close()     // Catch: java.io.IOException -> L4e java.lang.Throwable -> L57
            goto L4f
        L4e:
        L4f:
            if (r1 == 0) goto L54
            r1.close()     // Catch: java.io.IOException -> L54 java.lang.Throwable -> L57
        L54:
            throw r4     // Catch: java.lang.Throwable -> L57
        L55:
            monitor-exit(r0)
            return
        L57:
            r4 = move-exception
            monitor-exit(r0)
            throw r4
        */
        throw new UnsupportedOperationException("Method not decompiled: com.che168.autotradercloud.user.model.UserModel.saveUserPermissions(java.util.List):void");
    }

    /* JADX WARN: Multi-variable type inference failed */
    /* JADX WARN: Type inference failed for: r1v1, types: [java.io.File] */
    /* JADX WARN: Type inference failed for: r1v14 */
    /* JADX WARN: Type inference failed for: r1v2, types: [java.io.BufferedReader] */
    /* JADX WARN: Type inference failed for: r1v5 */
    private static synchronized List<UserPermissionsBean> getUserPermissions() {
        FileReader fileReader;
        BufferedReader bufferedReader;
        synchronized (UserModel.class) {
            ?? uPFile = getUPFile();
            try {
                if (uPFile != 0) {
                    try {
                        fileReader = new FileReader((File) uPFile);
                        try {
                            bufferedReader = new BufferedReader(fileReader);
                            String str = "";
                            while (true) {
                                try {
                                    String readLine = bufferedReader.readLine();
                                    if (readLine == null) {
                                        break;
                                    }
                                    str = str + readLine;
                                } catch (FileNotFoundException e) {
                                    e = e;
                                    e.printStackTrace();
                                    if (fileReader != null) {
                                        try {
                                            fileReader.close();
                                        } catch (IOException e2) {
                                            e2.printStackTrace();
                                        }
                                    }
                                    if (bufferedReader != null) {
                                        try {
                                            bufferedReader.close();
                                        } catch (IOException e3) {
                                            e = e3;
                                            e.printStackTrace();
                                            return null;
                                        }
                                    }
                                    return null;
                                } catch (IOException e4) {
                                    e = e4;
                                    e.printStackTrace();
                                    if (fileReader != null) {
                                        try {
                                            fileReader.close();
                                        } catch (IOException e5) {
                                            e5.printStackTrace();
                                        }
                                    }
                                    if (bufferedReader != null) {
                                        try {
                                            bufferedReader.close();
                                        } catch (IOException e6) {
                                            e = e6;
                                            e.printStackTrace();
                                            return null;
                                        }
                                    }
                                    return null;
                                }
                            }
                            if (!TextUtils.isEmpty(str)) {
                                List<UserPermissionsBean> list = (List) GsonUtil.fromJson(str, new TypeToken<ArrayList<UserPermissionsBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.22
                                }.getType());
                                try {
                                    fileReader.close();
                                } catch (IOException e7) {
                                    e7.printStackTrace();
                                }
                                try {
                                    bufferedReader.close();
                                } catch (IOException e8) {
                                    e8.printStackTrace();
                                }
                                return list;
                            }
                            try {
                                fileReader.close();
                            } catch (IOException e9) {
                                e9.printStackTrace();
                            }
                            try {
                                bufferedReader.close();
                            } catch (IOException e10) {
                                e = e10;
                                e.printStackTrace();
                                return null;
                            }
                        } catch (FileNotFoundException e11) {
                            e = e11;
                            bufferedReader = null;
                        } catch (IOException e12) {
                            e = e12;
                            bufferedReader = null;
                        } catch (Throwable th) {
                            th = th;
                            uPFile = 0;
                            if (fileReader != null) {
                                try {
                                    fileReader.close();
                                } catch (IOException e13) {
                                    e13.printStackTrace();
                                }
                            }
                            if (uPFile != 0) {
                                try {
                                    uPFile.close();
                                } catch (IOException e14) {
                                    e14.printStackTrace();
                                }
                            }
                            throw th;
                        }
                    } catch (FileNotFoundException e15) {
                        e = e15;
                        bufferedReader = null;
                        fileReader = null;
                    } catch (IOException e16) {
                        e = e16;
                        bufferedReader = null;
                        fileReader = null;
                    } catch (Throwable th2) {
                        fileReader = null;
                        th = th2;
                        uPFile = 0;
                    }
                }
                return null;
            } catch (Throwable th3) {
                th = th3;
            }
        }
    }

    private static File getUPFile() {
        File userFile = getUserFile();
        if (userFile != null) {
            File file = new File(userFile.getPath(), UPFileName);
            if (!file.exists()) {
                try {
                    file.createNewFile();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            return file;
        }
        return null;
    }

    private static SQLiteDatabase openMemberAuthDb() {
        AssetsDatabaseManager assetsDatabaseManager;
        if (ContextProvider.getContext() == null || (assetsDatabaseManager = AssetsDatabaseManager.getInstance(ContextProvider.getContext())) == null) {
            return null;
        }
        return assetsDatabaseManager.getDatabase(UserPermissionsDbHelp.DB_NAME);
    }

    private static void closeDatabase() {
        AssetsDatabaseManager assetsDatabaseManager;
        if (ContextProvider.getContext() == null || (assetsDatabaseManager = AssetsDatabaseManager.getInstance(ContextProvider.getContext())) == null) {
            return;
        }
        assetsDatabaseManager.closeDatabase(UserPermissionsDbHelp.DB_NAME);
    }

    public static boolean isInsurance() {
        CZYDealerBean dealerInfo = getDealerInfo();
        if (dealerInfo != null) {
            return dealerInfo.isInsurance();
        }
        return false;
    }

    public static void getDealerDiscountsInfo(String str, ResponseCallback<DealerDiscountsInfo> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(GET_DEALER_DICOUNTS_INFO);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<DealerDiscountsInfo>>() { // from class: com.che168.autotradercloud.user.model.UserModel.23
        }.getType());
    }

    public static void getCPLArrearsInfo(String str, ResponseCallback<Double> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        HttpUtil.Builder url = builder.tag(str).url(GET_CPL_ARREARS);
        url.param("dealerid", getDealerInfo().dealerid + "");
        doRequest(builder, responseCallback, new TypeToken<BaseResult<Double>>() { // from class: com.che168.autotradercloud.user.model.UserModel.24
        }.getType());
    }

    private static void getDealerSectionInfo(String str, ResponseCallback<DealerSectionInfoBean> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(GET_DEALER_INFO);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<DealerSectionInfoBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.25
        }.getType());
    }

    public static void loadDealerSectionInfo() {
        getDealerSectionInfo(null, new ResponseCallback<DealerSectionInfoBean>() { // from class: com.che168.autotradercloud.user.model.UserModel.26
            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void failed(int i, ApiException apiException) {
            }

            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void success(DealerSectionInfoBean dealerSectionInfoBean) {
                if (dealerSectionInfoBean != null) {
                    UserConfigUtil.asyncSaveString(UserModel.KEY_DEALER_SECTION_INFO, GsonUtil.toJson(dealerSectionInfoBean));
                }
            }
        });
    }

    public static DealerSectionInfoBean getDealerSectionInfo() {
        String string = UserConfigUtil.getString(KEY_DEALER_SECTION_INFO);
        if (ATCEmptyUtil.isEmpty((CharSequence) string)) {
            return null;
        }
        return (DealerSectionInfoBean) GsonUtil.fromJson(string, new TypeToken<DealerSectionInfoBean>() { // from class: com.che168.autotradercloud.user.model.UserModel.27
        }.getType());
    }

    public static boolean isNewPersonalManager() {
        return getDealerInfo().isPersonalManager();
    }

    public static boolean isPersonalManager() {
        return getDealerInfo().isPersonalManager();
    }

    public static String getUserMobileEncode() {
        return (getUserInfo() == null || TextUtils.isEmpty(getUserInfo().mobile)) ? "" : DesUtils.encode3Des("CsyM0b!le666CsyM0b!le666", "che168.!", getUserInfo().mobile);
    }

    public static void getMemberPhoto(String str, String str2, ResponseCallback<UserMemberHeadBean> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        HttpUtil.Builder url = builder.tag(str).url(GET_MEMBER_PHOTO);
        if (str2 == null) {
            str2 = "";
        }
        url.param(EmployeeTable.C_MEMBERID, str2);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<UserMemberHeadBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.28
        }.getType());
    }

    public static void getClubClubCertificationStatus(String str, ResponseCallback<JsonObject> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(GET_CLUB_CERTIFICATION);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<JsonObject>>() { // from class: com.che168.autotradercloud.user.model.UserModel.29
        }.getType());
    }

    public static void loadDealerSaleWeChat() {
        getDealerSaleWeChat(null, new ResponseCallback<DealerWeChatInfo>() { // from class: com.che168.autotradercloud.user.model.UserModel.30
            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void failed(int i, ApiException apiException) {
            }

            @Override // com.che168.autotradercloud.base.httpNew.ResponseCallback
            public void success(DealerWeChatInfo dealerWeChatInfo) {
                if (dealerWeChatInfo != null) {
                    UserConfigUtil.saveString(UserModel.KEY_DEALER_WE_CHAT_CODE, dealerWeChatInfo.getWeixincode());
                }
            }
        });
    }

    public static void getDealerSaleWeChat(String str, ResponseCallback<DealerWeChatInfo> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(GET_DEALER_SALE_WE_CHAT);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<DealerWeChatInfo>>() { // from class: com.che168.autotradercloud.user.model.UserModel.31
        }.getType());
    }

    public static void postDealerSaleWeChat(String str, String str2, ResponseCallback<JsonObject> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).method(HttpUtil.Method.POST).url(POST_DEALER_SALE_WE_CHAT).param("weixincode", str2);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<JsonObject>>() { // from class: com.che168.autotradercloud.user.model.UserModel.32
        }.getType());
    }

    public static void postEditMemberInfo(String str, TreeMap<String, String> treeMap, ResponseCallback<JsonObject> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).method(HttpUtil.Method.POST).url(EDIT_MEMBER_INFO).params(treeMap);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<JsonObject>>() { // from class: com.che168.autotradercloud.user.model.UserModel.33
        }.getType());
    }

    public static boolean hasRightByType(Context context, MemberRightType memberRightType) {
        boolean hasRightByType = getDealerInfo().hasRightByType(memberRightType);
        if (!hasRightByType && context != null) {
            GuideConfigBean memberRightConfig = getDealerCacheInfo().getMemberRightConfig(memberRightType);
            if (memberRightConfig != null) {
                JSUrl jSUrl = new JSUrl(memberRightConfig.getApp_target_url());
                jSUrl.addParams("imgurl", memberRightConfig.getAppimg());
                jSUrl.addParams("producttype", Integer.valueOf(memberRightConfig.getProducttype()));
                jSUrl.addParams("isselling", Integer.valueOf(memberRightConfig.getIsselling()));
                JumpPageController.goOrdinaryWebActivity(context, jSUrl.getUrl(), "");
            } else {
                JumpPageController.go2020MemberProductIntroductions(context, memberRightType.getProductType(), "");
            }
        }
        return hasRightByType;
    }

    public static void getWelfaredes(String str, ResponseCallback<WelfaredesBean> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).url(GET_WELFAREDES);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<WelfaredesBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.34
        }.getType());
    }

    public static void showForcedPasswordChangeDialog(final Context context, final String str, final String str2, final UserBean userBean) {
        if (AppManager.getInstance().getTopActivity() instanceof PasswordModifyActivity) {
            return;
        }
        DialogUtils.showConfirm(context, "为了您的账户安全，请修改登录密码！", "去修改", new View.OnClickListener() { // from class: com.che168.autotradercloud.user.model.UserModel.35
            @Override // android.view.View.OnClickListener
            public void onClick(View view) {
                JumpPageController.goPasswordModify(context, str, str2, userBean, true);
            }
        });
    }

    public static void loginByMobile(String str, String str2, String str3, ResponseCallback<UserBean> responseCallback) {
        HttpUtil.Builder builder = new HttpUtil.Builder();
        builder.tag(str).method(HttpUtil.Method.POST).signType(1).url(LOGIN_BY_MOBILE).param(EmployeeTable.C_MOBILE, str2).param("code", str3);
        doRequest(builder, responseCallback, new TypeToken<BaseResult<UserBean>>() { // from class: com.che168.autotradercloud.user.model.UserModel.36
        }.getType());
    }

    public static void login(String str, String str2, String str3, boolean z, SelectCityBean selectCityBean, String str4, String str5, ResponseCallback<UserBean> responseCallback) {
        long j;
        long j2;
        long j3;
        if (z) {
            if (selectCityBean != null) {
                j = selectCityBean.getPI();
                j2 = selectCityBean.getCI();
                j3 = selectCityBean.getCountyId();
            } else {
                j = 0;
                j2 = 0;
                j3 = 0;
            }
            LoginModel.INSTANCE.loginByMobile(str, str2, str3, j, j2, j3, str4, str5, responseCallback);
            return;
        }
        loginByPassword(str, str2, str3, str4, str5, responseCallback);
    }

    public static boolean hasStoreCarFunction() {
        return getDealerInfo().is21NewPayMode() && getDealerCacheInfo().hasStoreCarFunc();
    }
}
