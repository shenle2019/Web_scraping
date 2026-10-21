package com.shenjiahang.netapp;

import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.gson.Gson;
import com.shenjiahang.netapp.api.ApiFactory;
import com.shenjiahang.netapp.model.Film;
import com.shenjiahang.netapp.model.FilmResult;
import com.shenjiahang.netapp.ui.FilmAdapter;
import com.shenjiahang.netapp.util.AppPrefs;

import java.util.ArrayList;
import java.util.List;

import okhttp3.ResponseBody;
import retrofit2.Response;

/**
 * 列表页：Retrofit 发请求 -> Gson 解析 -> ListView + BaseAdapter + Glide 渲染。
 * 这里没有写任何 header，token 与签名头全部由 SignInterceptor 补齐。
 */
public class IndexActivity extends AppCompatActivity {

    private static final String TAG = "NetApp";

    private final Gson gson = new Gson();
    private FilmAdapter adapter;
    private TextView tvTip;
    private TextView tvCount;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_index);

        tvTip = findViewById(R.id.tv_tip);
        tvCount = findViewById(R.id.tv_count);
        ListView listView = findViewById(R.id.lv_films);
        adapter = new FilmAdapter(this);
        listView.setAdapter(adapter);

        findViewById(R.id.btn_logout).setOnClickListener(v -> {
            AppPrefs.clear(this);
            toast("已清除 token，请重新登录");
            finish();
        });

        String user = AppPrefs.getUser(this);
        String token = AppPrefs.getToken(this);
        tvTip.setText("user=" + user + "  token=" + mask(token)
                + "\nheader 由 SignInterceptor 注入：ctime / hsign / Authorization");

        loadFilms();
    }

    private void loadFilms() {
        new Thread(() -> {
            try {
                Response<ResponseBody> resp = ApiFactory.get().films().execute();
                String body = resp.body() == null ? "" : resp.body().string();
                Log.i(TAG, "films <- HTTP " + resp.code() + " " + body);

                if (resp.code() == 401) {
                    runOnUiThread(() -> {
                        toast("token 无效或已过期，请重新登录");
                        finish();
                    });
                    return;
                }

                FilmResult result = gson.fromJson(body, FilmResult.class);
                if (result == null || result.data == null) {
                    runOnUiThread(() -> tvCount.setText("响应解析失败：data 为空"));
                    return;
                }
                List<Film> films = new ArrayList<>(result.data);
                runOnUiThread(() -> {
                    adapter.setData(films);
                    tvCount.setText("共 " + films.size() + " 部电影（code=" + result.code + "）");
                    if (TextUtils.isEmpty(AppPrefs.getToken(this))) {
                        tvCount.append("  ⚠ token 未落盘");
                    }
                });
            } catch (Exception e) {
                Log.e(TAG, "load films failed", e);
                runOnUiThread(() -> {
                    tvCount.setText("请求异常: " + e);
                    toast("加载失败，检查后端是否启动");
                });
            }
        }).start();
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
