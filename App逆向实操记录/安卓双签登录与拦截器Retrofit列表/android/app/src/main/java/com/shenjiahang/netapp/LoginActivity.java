package com.shenjiahang.netapp;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.gson.Gson;
import com.google.gson.JsonSyntaxException;
import com.shenjiahang.netapp.api.ApiFactory;
import com.shenjiahang.netapp.api.ApiService;
import com.shenjiahang.netapp.model.LoginResult;
import com.shenjiahang.netapp.net.Http;
import com.shenjiahang.netapp.net.NetConfig;
import com.shenjiahang.netapp.net.Signer;
import com.shenjiahang.netapp.util.AppPrefs;
import com.shenjiahang.netapp.util.Md5Utils;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

import okhttp3.FormBody;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.ResponseBody;

/**
 * 登录页：两条链路（OkHttp 手写 / Retrofit 注解）共用同一套签名与拦截器。
 */
public class LoginActivity extends AppCompatActivity {

    private static final String TAG = "NetApp";
    private static final String DEFAULT_USER = "justin";
    private static final String DEFAULT_PWD = "123456";

    private EditText etUser;
    private EditText etPwd;
    private TextView tvLog;
    private ScrollView svLog;
    private final Gson gson = new Gson();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        etUser = findViewById(R.id.et_user);
        etPwd = findViewById(R.id.et_pwd);
        tvLog = findViewById(R.id.tv_log);
        svLog = findViewById(R.id.sv_log);

        etUser.setText(DEFAULT_USER);
        etPwd.setText(DEFAULT_PWD);

        append("BaseURL : " + NetConfig.BASE_URL);
        append("body   sign = md5(t1 + user + md5(pwd))");
        append("header hsign = md5(ctime + \"" + NetConfig.SALT + "\")");
        append("prefs 路径 : /data/data/" + getPackageName() + "/shared_prefs/" + NetConfig.SP_NAME + ".xml");
        if (AppPrefs.hasToken(this)) {
            append("已缓存 token : " + mask(AppPrefs.getToken(this)) + "（user=" + AppPrefs.getUser(this) + "）");
        }

        Button btnLogin = findViewById(R.id.btn_login);
        Button btnRetrofit = findViewById(R.id.btn_retrofit);
        Button btnReset = findViewById(R.id.btn_reset);

        btnLogin.setOnClickListener(v -> doLoginByOkHttp());
        btnRetrofit.setOnClickListener(v -> doLoginByRetrofit());
        btnReset.setOnClickListener(v -> {
            etUser.setText(DEFAULT_USER);
            etPwd.setText(DEFAULT_PWD);
            tvLog.setText("");
            AppPrefs.clear(this);
            append("已重置输入框并清空本地 token");
        });
    }

    // ------------------------------------------------------------------ OkHttp

    private void doLoginByOkHttp() {
        String user = etUser.getText().toString().trim();
        String rawPwd = etPwd.getText().toString();
        if (TextUtils.isEmpty(user) || TextUtils.isEmpty(rawPwd)) {
            toast("用户名/密码不能为空");
            return;
        }

        final String t1 = Signer.nowSeconds();
        final String pwdMd5 = Md5Utils.md5(rawPwd);
        final String sign = Signer.bodySign(user, rawPwd, t1);

        append("");
        append("==== OkHttp /login ====");
        append("t1      = " + t1);
        append("pwd     = md5(" + rawPwd + ") = " + pwdMd5);
        append("sign    = md5(" + t1 + " + " + user + " + " + pwdMd5 + ") = " + sign);
        append("header  = ctime / hsign，由 SignInterceptor 注入");

        new Thread(() -> {
            try {
                FormBody form = new FormBody.Builder()
                        .add("user", user)
                        .add("pwd", pwdMd5)
                        .add("sign", sign)
                        .add("t1", t1)
                        .build();
                Request request = new Request.Builder()
                        .url(NetConfig.BASE_URL + "login")
                        .post(form)
                        .build();

                try (Response response = Http.get().newCall(request).execute()) {
                    String body = response.body() == null ? "" : response.body().string();
                    String line = "HTTP " + response.code()
                            + "  X-Server-Time=" + response.header("X-Server-Time")
                            + "\n" + body;
                    Log.i(TAG, line);
                    runOnUiThread(() -> append(line));
                    handleLoginResult(body, user, "OkHttp");
                }
            } catch (Exception e) {
                Log.e(TAG, "okhttp login failed", e);
                runOnUiThread(() -> append("请求异常: " + e));
            }
        }).start();
    }

    // ---------------------------------------------------------------- Retrofit

    private void doLoginByRetrofit() {
        String user = etUser.getText().toString().trim();
        String rawPwd = etPwd.getText().toString();
        if (TextUtils.isEmpty(user) || TextUtils.isEmpty(rawPwd)) {
            toast("用户名/密码不能为空");
            return;
        }

        final String t1 = Signer.nowSeconds();
        final String pwdMd5 = Md5Utils.md5(rawPwd);
        final String sign = Signer.bodySign(user, rawPwd, t1);

        append("");
        append("==== Retrofit /login ====");
        append("POST " + NetConfig.BASE_URL + "login  (@FormUrlEncoded + @Field)");
        append("t1=" + t1 + " sign=" + sign);

        new Thread(() -> {
            try {
                ApiService api = ApiFactory.get();
                retrofit2.Response<ResponseBody> resp = api.login(user, pwdMd5, sign, t1).execute();
                String body = resp.body() == null ? "" : resp.body().string();
                String line = "HTTP " + resp.code() + "\n" + body;
                Log.i(TAG, line);
                runOnUiThread(() -> append(line));
                handleLoginResult(body, user, "Retrofit");
            } catch (Exception e) {
                Log.e(TAG, "retrofit login failed", e);
                runOnUiThread(() -> append("请求异常: " + e));
            }
        }).start();
    }

    // ------------------------------------------------------------------ 公共

    private void handleLoginResult(String body, String user, String via) {
        LoginResult result;
        try {
            result = gson.fromJson(body, LoginResult.class);
        } catch (JsonSyntaxException e) {
            runOnUiThread(() -> append("JSON 解析失败: " + e.getMessage()));
            return;
        }
        if (result == null) {
            runOnUiThread(() -> append("响应为空，检查服务端是否已启动"));
            return;
        }
        if (result.code == 100 && !TextUtils.isEmpty(result.token)) {
            AppPrefs.saveLogin(this, user, result.token);
            runOnUiThread(() -> {
                append("登录成功(" + via + ")，token 已写入 SharedPreferences");
                toast("登录成功");
                startActivity(new Intent(LoginActivity.this, IndexActivity.class));
            });
        } else {
            runOnUiThread(() -> {
                append("登录失败(" + via + ") code=" + result.code + " msg=" + result.msg);
                toast("登录失败: " + result.msg);
            });
        }
    }

    private void append(String text) {
        String ts = new SimpleDateFormat("HH:mm:ss", Locale.CHINA).format(new Date());
        tvLog.append("[" + ts + "] " + text + "\n");
        svLog.post(() -> svLog.fullScroll(View.FOCUS_DOWN));
    }

    private void toast(String text) {
        Toast.makeText(this, text, Toast.LENGTH_SHORT).show();
    }

    private static String mask(String token) {
        if (token == null || token.length() <= 8) {
            return String.valueOf(token);
        }
        return token.substring(0, 8) + "..." + token.substring(token.length() - 4);
    }
}
