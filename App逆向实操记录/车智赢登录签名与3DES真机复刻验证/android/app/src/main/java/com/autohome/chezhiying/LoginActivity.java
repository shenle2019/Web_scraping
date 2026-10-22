package com.autohome.chezhiying;

import android.app.Activity;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import com.autohome.ahkit.utils.SecurityUtil;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.Map;
import java.util.TreeMap;

/**
 * 复刻车智赢登录页：输入账号密码，组公共参数 -> 算 pwd/udid/_sign -> POST 登录接口。
 * 界面用纯代码搭，避免额外依赖，方便反编译后阅读。
 */
public class LoginActivity extends Activity {

    private static final String TAG = "CheZhiYing";
    private static final String LOGIN_PATH = "/tradercloud/sealed/login/login.ashx";

    private EditText etUser;
    private EditText etPwd;
    private EditText etServer;
    private TextView tvResult;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = (int) (16 * getResources().getDisplayMetrics().density);
        root.setPadding(pad, pad, pad, pad);

        etUser = new EditText(this);
        etUser.setHint("用户名（手机号）");
        etUser.setText("13800138000");
        root.addView(etUser);

        etPwd = new EditText(this);
        etPwd.setHint("密码");
        etPwd.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        etPwd.setText("123456");
        root.addView(etPwd);

        etServer = new EditText(this);
        etServer.setHint("服务端地址");
        etServer.setText("http://192.168.31.220:8000");
        root.addView(etServer);

        Button btnLogin = new Button(this);
        btnLogin.setText("登录");
        root.addView(btnLogin);

        ScrollView scroll = new ScrollView(this);
        tvResult = new TextView(this);
        tvResult.setText("等待登录");
        scroll.addView(tvResult);
        root.addView(scroll);

        btnLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                doLogin();
            }
        });

        setContentView(root);
    }

    private void doLogin() {
        final String user = etUser.getText().toString().trim();
        final String pwd = etPwd.getText().toString().trim();
        final String server = etServer.getText().toString().trim();

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    TreeMap<String, String> params = new TreeMap<String, String>();
                    params.put("username", user);
                    params.put("pwd", SecurityUtil.encodeMD5(pwd));
                    params.put("signkey", "");
                    params.put("type", "");
                    new LaunchModel().initRequestCommonParams(1, params, LoginActivity.this);

                    StringBuilder body = new StringBuilder();
                    for (Map.Entry<String, String> e : params.entrySet()) {
                        if (body.length() > 0) {
                            body.append('&');
                        }
                        body.append(URLEncoder.encode(e.getKey(), "UTF-8"));
                        body.append('=');
                        body.append(URLEncoder.encode(e.getValue(), "UTF-8"));
                    }
                    Log.i(TAG, "POST " + server + LOGIN_PATH);
                    Log.i(TAG, "body=" + body);

                    String resp = post(server + LOGIN_PATH, body.toString());
                    Log.i(TAG, "response=" + resp);
                    show("请求参数：\n" + params + "\n\n服务端返回：\n" + resp);
                } catch (Exception e) {
                    Log.e(TAG, "login failed", e);
                    show("登录异常：" + e);
                }
            }
        }).start();
    }

    private String post(String url, String body) throws Exception {
        HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
        conn.setRequestMethod("POST");
        conn.setConnectTimeout(8000);
        conn.setReadTimeout(8000);
        conn.setDoOutput(true);
        conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        OutputStream os = conn.getOutputStream();
        os.write(body.getBytes("UTF-8"));
        os.flush();
        os.close();

        int code = conn.getResponseCode();
        BufferedReader reader = new BufferedReader(new InputStreamReader(
                code >= 400 ? conn.getErrorStream() : conn.getInputStream(), "UTF-8"));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            sb.append(line);
        }
        reader.close();
        return "HTTP " + code + " " + sb;
    }

    private void show(final String text) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                tvResult.setText(text);
            }
        });
    }
}
