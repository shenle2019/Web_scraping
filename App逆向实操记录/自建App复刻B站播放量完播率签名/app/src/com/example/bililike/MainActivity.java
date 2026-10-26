package com.example.bililike;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.Locale;

/**
 * 自建复刻 App 的调试面板。
 * 启动后自动跑一遍完整链路（设备指纹 -> click -> heartbeat 开始/结束），
 * 结果同时打到 logcat（tag=BiliReplica）与屏幕，便于 adb 侧验收。
 *
 * 仅用于本地复刻验证，服务端是本机 mock，不连接任何线上服务。
 */
public class MainActivity extends Activity {

    private static final String TAG = "BiliReplica";
    private static final long AID = 8848L;
    private static final long CID = 175882888L;
    private static final int DURATION = 600;

    private final Handler ui = new Handler(Looper.getMainLooper());
    private TextView logView;
    private EditText serverView;
    private DeviceProfile profile;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(buildUi());
        new Thread(new Runnable() {
            @Override
            public void run() {
                runSelfTest();
            }
        }, "selftest").start();
    }

    private View buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(24, 24, 24, 24);

        TextView title = new TextView(this);
        title.setText("BiliReplica 本地复刻面板");
        title.setTextSize(18);
        root.addView(title);

        serverView = new EditText(this);
        serverView.setText("http://127.0.0.1:8899");
        serverView.setTextSize(12);
        root.addView(serverView);

        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        Button click = new Button(this);
        click.setText("click 上报");
        click.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        sendClick();
                    }
                }).start();
            }
        });
        Button beat = new Button(this);
        beat.setText("心跳上报");
        beat.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        sendHeartbeatPair();
                    }
                }).start();
            }
        });
        row.addView(click);
        row.addView(beat);
        root.addView(row);

        ScrollView scroll = new ScrollView(this);
        logView = new TextView(this);
        logView.setTextSize(11);
        logView.setGravity(Gravity.START);
        scroll.addView(logView);
        root.addView(scroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));
        return root;
    }

    private void log(String line) {
        Log.i(TAG, line);
        final String text = line + "\n";
        ui.post(new Runnable() {
            @Override
            public void run() {
                logView.append(text);
            }
        });
    }

    private String baseUrl() {
        return serverView.getText().toString().trim();
    }

    private static boolean verified(String resp) {
        // mock server 的 json.dumps 默认带空格，统一去空格再判断
        return resp.replace(" ", "").contains("\"verified\":true");
    }

    private void runSelfTest() {
        int pass = 0;
        int total = 0;
        log("SELFTEST|00|start|sdk=" + android.os.Build.VERSION.SDK_INT);
        try {
            profile = DeviceProfile.create(this);
            log("SELFTEST|01|profile|buvid=" + profile.buvid);
            log("SELFTEST|01|profile|device_id=" + profile.deviceId);
            log("SELFTEST|01|profile|session_id=" + profile.sessionId);
            log("SELFTEST|01|profile|fp_local=" + profile.fpLocal);
            log("SELFTEST|01|profile|fp_remote=" + profile.fpRemote);

            String probe = "native_parity_probe";
            String nativeSign = BiliSign.nativeSign(probe);
            String javaSign = BiliSign.javaSign(probe);
            String expected = BiliSign.expectedSign(probe);
            boolean parity = nativeSign.equals(javaSign) && javaSign.equals(expected);
            total++;
            if (parity) {
                pass++;
            }
            log("SELFTEST|02|native_parity|native=" + nativeSign
                    + " java=" + javaSign + " expected=" + expected
                    + "|" + (parity ? "PASS" : "FAIL"));

            total++;
            if (sendClick()) {
                pass++;
            }
            Thread.sleep(1200);
            total++;
            if (sendHeartbeatPair()) {
                pass++;
            }
            log(String.format(Locale.US, "SELFTEST|99|done|%d/%d|%s",
                    pass, total, pass == total ? "PASS" : "FAIL"));
        } catch (Throwable t) {
            log("SELFTEST|99|done|exception|FAIL:" + Log.getStackTraceString(t));
        }
    }

    private boolean sendClick() {
        try {
            ClickReport.Payload p = ClickReport.build(profile, AID, CID, DURATION);
            log("CLICK|plain=" + p.plain);
            log("CLICK|sign=" + p.sign);
            log("CLICK|cipher_hex=" + BiliCrypto.hex(p.body));
            String resp = HttpUtil.post(baseUrl() + ClickReport.PATH,
                    ReportInterceptor.headers(profile), p.body, ClickReport.CONTENT_TYPE);
            boolean ok = verified(resp);
            log("CLICK|resp=" + resp + "|" + (ok ? "PASS" : "FAIL"));
            return ok;
        } catch (Throwable t) {
            log("CLICK|error=" + Log.getStackTraceString(t));
            return false;
        }
    }

    private boolean sendHeartbeatPair() {
        boolean ok = true;
        try {
            long startTs = System.currentTimeMillis() - (DURATION + 5) * 1000L;
            String session = HeartbeatReport.newSession(profile);

            HeartbeatReport.Payload start = HeartbeatReport.build(
                    profile, AID, CID, DURATION, startTs, false, session);
            log("HEARTBEAT|start|sign=" + start.sign);
            String resp1 = HttpUtil.post(baseUrl() + HeartbeatReport.PATH,
                    ReportInterceptor.headers(profile), start.body,
                    HeartbeatReport.CONTENT_TYPE);
            boolean ok1 = verified(resp1);
            log("HEARTBEAT|start|resp=" + resp1 + "|" + (ok1 ? "PASS" : "FAIL"));
            ok &= ok1;

            Thread.sleep(1200);

            HeartbeatReport.Payload end = HeartbeatReport.build(
                    profile, AID, CID, DURATION, startTs, true, session);
            log("HEARTBEAT|end|sign=" + end.sign);
            String resp2 = HttpUtil.post(baseUrl() + HeartbeatReport.PATH,
                    ReportInterceptor.headers(profile), end.body,
                    HeartbeatReport.CONTENT_TYPE);
            boolean ok2 = verified(resp2);
            log("HEARTBEAT|end|resp=" + resp2 + "|" + (ok2 ? "PASS" : "FAIL"));
            ok &= ok2;
        } catch (Throwable t) {
            log("HEARTBEAT|error=" + Log.getStackTraceString(t));
            ok = false;
        }
        return ok;
    }
}
