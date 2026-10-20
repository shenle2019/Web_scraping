package com.shenjiahang.logindemo;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;

/**
 * day09 登录案例联调 Demo：
 * 真机通过 adb reverse tcp:8080 tcp:8080 访问本机 Flask 服务，
 * 用最原始的 HttpURLConnection 提交表单，观察 code=100 / code=101 两种返回。
 */
public class LoginActivity extends Activity {

    private static final String TAG = "LoginDemo";
    private static final String LOGIN_URL = "http://127.0.0.1:8080/login";
    private static final String PHOTO_URL = "http://127.0.0.1:8080/photo";

    private EditText etUsername;
    private EditText etPassword;
    private TextView tvResult;
    private Button btnLogin;
    private Button btnWrong;
    private Button btnPhoto;
    private ImageView ivPhoto;

    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        etUsername = findViewById(R.id.et_username);
        etPassword = findViewById(R.id.et_password);
        tvResult = findViewById(R.id.tv_result);
        btnLogin = findViewById(R.id.btn_login);
        btnWrong = findViewById(R.id.btn_wrong);
        btnPhoto = findViewById(R.id.btn_photo);
        ivPhoto = findViewById(R.id.iv_photo);

        btnLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                submit(etUsername.getText().toString(), etPassword.getText().toString());
            }
        });

        // 固定错误密码，用来验证服务端 code=101 分支
        btnWrong.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                submit(etUsername.getText().toString(), "wrong-pass");
            }
        });

        // day09「显示网络图片」环节：子线程下载，主线程 setImageBitmap
        btnPhoto.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                loadNetworkPhoto();
            }
        });

        Log.i(TAG, "onCreate, target=" + LOGIN_URL);
        tvResult.setText("目标地址：" + LOGIN_URL + "\n等待点击登录……");
    }

    private void loadNetworkPhoto() {
        btnPhoto.setEnabled(false);
        btnPhoto.setText("图片下载中……");
        Log.i(TAG, "load photo start, url=" + PHOTO_URL);

        new Thread(new Runnable() {
            @Override
            public void run() {
                final long begin = System.currentTimeMillis();
                Bitmap bitmap = null;
                String error = null;
                try {
                    HttpURLConnection conn = (HttpURLConnection) new URL(PHOTO_URL).openConnection();
                    conn.setConnectTimeout(8000);
                    conn.setReadTimeout(8000);
                    conn.setRequestProperty("User-Agent", "LoginDemo");
                    int httpCode = conn.getResponseCode();
                    if (httpCode == 200) {
                        InputStream in = conn.getInputStream();
                        bitmap = BitmapFactory.decodeStream(in);
                        in.close();
                    } else {
                        error = "HTTP " + httpCode;
                    }
                    conn.disconnect();
                } catch (Exception e) {
                    error = e.getClass().getSimpleName() + ": " + e.getMessage();
                }
                final Bitmap result = bitmap;
                final String fail = error;
                final long cost = System.currentTimeMillis() - begin;
                Log.i(TAG, "load photo done, bitmap=" + (result == null ? "null" : result.getWidth() + "x" + result.getHeight())
                        + " cost=" + cost + "ms" + (fail == null ? "" : " error=" + fail));

                mainHandler.post(new Runnable() {
                    @Override
                    public void run() {
                        btnPhoto.setEnabled(true);
                        btnPhoto.setText(getString(R.string.btn_photo));
                        if (result != null) {
                            ivPhoto.setVisibility(View.VISIBLE);
                            ivPhoto.setImageBitmap(result);
                            tvResult.setText("网络图片已加载：" + result.getWidth() + "×" + result.getHeight()
                                    + "（" + cost + "ms）\n来源：" + PHOTO_URL);
                        } else {
                            tvResult.setText("图片加载失败：" + fail);
                        }
                    }
                });
            }
        }, "photo-thread").start();
    }

    private void submit(final String username, final String password) {
        btnLogin.setEnabled(false);
        btnWrong.setEnabled(false);
        tvResult.setText("请求中……\nPOST " + LOGIN_URL
                + "\nusername=" + username + "&password=" + password);
        Log.i(TAG, "submit start, username=" + username);

        new Thread(new Runnable() {
            @Override
            public void run() {
                final long begin = System.currentTimeMillis();
                String body;
                int httpCode;
                try {
                    HttpURLConnection conn = (HttpURLConnection) new URL(LOGIN_URL).openConnection();
                    conn.setRequestMethod("POST");
                    conn.setConnectTimeout(8000);
                    conn.setReadTimeout(8000);
                    conn.setDoOutput(true);
                    conn.setRequestProperty("Content-Type",
                            "application/x-www-form-urlencoded; charset=UTF-8");

                    String form = "username=" + URLEncoder.encode(username, "UTF-8")
                            + "&password=" + URLEncoder.encode(password, "UTF-8");
                    OutputStream os = conn.getOutputStream();
                    os.write(form.getBytes("UTF-8"));
                    os.flush();
                    os.close();

                    httpCode = conn.getResponseCode();
                    InputStream in = httpCode >= 400 ? conn.getErrorStream() : conn.getInputStream();
                    body = readAll(in);
                    conn.disconnect();
                } catch (Exception e) {
                    httpCode = -1;
                    body = e.getClass().getSimpleName() + ": " + e.getMessage();
                }
                final int code = httpCode;
                final String text = body;
                final long cost = System.currentTimeMillis() - begin;
                Log.i(TAG, "response http=" + code + " body=" + text + " cost=" + cost + "ms");

                mainHandler.post(new Runnable() {
                    @Override
                    public void run() {
                        tvResult.setText("HTTP " + code + "（" + cost + "ms）\n\n" + text);
                        btnLogin.setEnabled(true);
                        btnWrong.setEnabled(true);
                    }
                });
            }
        }, "login-thread").start();
    }

    private static String readAll(InputStream in) throws Exception {
        if (in == null) {
            return "(empty stream)";
        }
        BufferedReader reader = new BufferedReader(new InputStreamReader(in, "UTF-8"));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            sb.append(line).append('\n');
        }
        reader.close();
        return sb.toString().trim();
    }
}
