package com.repl.shihuo;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.method.ScrollingMovementMethod;
import android.util.Log;
import android.widget.EditText;
import android.widget.TextView;

import com.repl.shihuo.net.Api;
import com.repl.shihuo.update.UpdateChecker;
import com.repl.shihuo.update.UpdateDialog;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {

    private static final String TAG = "MainActivity";

    private final ExecutorService pool = Executors.newSingleThreadExecutor();
    private final Handler ui = new Handler(Looper.getMainLooper());
    private final SimpleDateFormat fmt = new SimpleDateFormat("HH:mm:ss", Locale.CHINA);

    private TextView logView;
    private TextView goodsView;
    private EditText keywordView;
    private String currentGoodsId = "379112";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        logView = findViewById(R.id.log);
        goodsView = findViewById(R.id.currentGoods);
        keywordView = findViewById(R.id.keyword);
        logView.setMovementMethod(new ScrollingMovementMethod());

        findViewById(R.id.btnSearchOld).setOnClickListener(v -> runTask("搜索(老接口)", () -> {
            String body = Api.searchOld(keyword());
            JSONObject json = new JSONObject(body);
            JSONArray list = json.optJSONObject("data") == null ? null
                    : json.getJSONObject("data").optJSONArray("list");
            if (list != null && list.length() > 0) {
                setGoodsId(list.getJSONObject(0).optString("goods_id", currentGoodsId));
            }
            return body;
        }));

        findViewById(R.id.btnSearchNew).setOnClickListener(v ->
                runTask("搜索(新接口·风控头)", () -> Api.searchNew(keyword())));

        findViewById(R.id.btnDetailOld).setOnClickListener(v ->
                runTask("详情(老接口·加密)", () -> Api.detailOld(currentGoodsId)));

        findViewById(R.id.btnDetailNew).setOnClickListener(v ->
                runTask("详情(新接口·明文)", () -> Api.detailNew(currentGoodsId)));

        findViewById(R.id.btnContrast).setOnClickListener(v ->
                runTask("对照请求(走系统代理)", Api::contrast));

        findViewById(R.id.btnClear).setOnClickListener(v -> logView.setText(""));

        checkUpdate();
    }

    private void checkUpdate() {
        append(">>> 版本检查 /app/version");
        UpdateChecker.check((force, latest) -> {
            append("服务端最新版本 " + latest + (force ? "，强制更新" : "，无需更新"));
            if (force) {
                append("调用 UpdateDialog.show()，弹窗不可取消（可用 Frida 拦截）");
                UpdateDialog.show(this, latest);
            }
        });
    }

    private interface Task {
        String run() throws Exception;
    }

    private void runTask(String title, Task task) {
        append(">>> " + title);
        pool.execute(() -> {
            try {
                String result = task.run();
                append("<<< " + title + "\n" + pretty(result));
            } catch (Exception e) {
                Log.e(TAG, title + " 失败", e);
                append("!!! " + title + " 失败: " + e);
            }
        });
    }

    private String keyword() {
        return keywordView.getText().toString().trim();
    }

    private void setGoodsId(String goodsId) {
        currentGoodsId = goodsId;
        ui.post(() -> goodsView.setText(goodsId));
    }

    private void append(String text) {
        ui.post(() -> logView.append("[" + fmt.format(new Date()) + "] " + text + "\n"));
    }

    private String pretty(String body) {
        String out = body;
        try {
            out = new JSONObject(body).toString(2);
        } catch (Exception ignored) {
            // 非 JSON 原样输出
        }
        return out.length() > 4000 ? out.substring(0, 4000) + "\n...(截断)" : out;
    }
}
