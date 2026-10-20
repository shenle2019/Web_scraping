package com.shenjiahang.babyalbum;

import android.os.Bundle;
import android.view.HapticFeedbackConstants;
import android.view.animation.DecelerateInterpolator;
import android.view.animation.LinearInterpolator;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.card.MaterialCardView;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

/**
 * 「沈嘉杭呀」宝宝写真随机看图。
 *
 * 核心逻辑：
 * 1. 图片全部打包在 res/drawable-nodpi，运行时零网络依赖；
 * 2. 用“洗牌袋”随机：一轮内不重复，洗牌后首张避开上一次的图；
 * 3. 切换时做淡出/缩放 + 缓慢推镜（Ken Burns），点击卡片或按钮都能换图。
 */
public class MainActivity extends AppCompatActivity {

    private static final int[] PHOTOS = {
            R.drawable.photo_01, R.drawable.photo_02, R.drawable.photo_03,
            R.drawable.photo_04, R.drawable.photo_05, R.drawable.photo_06,
            R.drawable.photo_07, R.drawable.photo_08, R.drawable.photo_09,
            R.drawable.photo_10, R.drawable.photo_11
    };

    private final Random random = new Random();
    private final List<Integer> bag = new ArrayList<>();

    private MaterialCardView cardPhoto;
    private ImageView ivPhoto;
    private TextView tvChip;
    private Button btnNext;

    private int current = -1;
    private boolean switching = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        cardPhoto = findViewById(R.id.cardPhoto);
        ivPhoto = findViewById(R.id.ivPhoto);
        tvChip = findViewById(R.id.tvChip);
        btnNext = findViewById(R.id.btnNext);

        // 先放一张图，卡片整体做入场动画
        current = nextIndex();
        applyPhoto(current);
        cardPhoto.setAlpha(0f);
        cardPhoto.setTranslationY(dp(22));
        cardPhoto.animate()
                .alpha(1f)
                .translationY(0f)
                .setDuration(520)
                .setInterpolator(new DecelerateInterpolator())
                .start();

        btnNext.setOnClickListener(v -> {
            v.performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY);
            v.animate().scaleX(0.96f).scaleY(0.96f).setDuration(70)
                    .withEndAction(() -> v.animate().scaleX(1f).scaleY(1f)
                            .setDuration(150).start())
                    .start();
            showNext();
        });
        cardPhoto.setOnClickListener(v -> showNext());
    }

    /** 淡出旧图 -> 换图 -> 淡入，同时重新开始推镜动画 */
    private void showNext() {
        if (switching) {
            return;
        }
        switching = true;
        cardPhoto.animate()
                .alpha(0f)
                .scaleX(0.97f)
                .scaleY(0.97f)
                .setDuration(120)
                .withEndAction(() -> {
                    current = nextIndex();
                    applyPhoto(current);
                    cardPhoto.animate()
                            .alpha(1f)
                            .scaleX(1f)
                            .scaleY(1f)
                            .setDuration(260)
                            .setInterpolator(new DecelerateInterpolator())
                            .withEndAction(() -> switching = false)
                            .start();
                })
                .start();
    }

    private void applyPhoto(int index) {
        ivPhoto.animate().cancel();
        ivPhoto.setScaleX(1f);
        ivPhoto.setScaleY(1f);
        ivPhoto.setImageResource(PHOTOS[index]);
        ivPhoto.setContentDescription(getString(R.string.photo_desc, index + 1));
        tvChip.setText(getString(R.string.chip_format, index + 1, PHOTOS.length));

        // 计数胶囊弹一下
        tvChip.setScaleX(0.9f);
        tvChip.setScaleY(0.9f);
        tvChip.animate().scaleX(1f).scaleY(1f).setDuration(220).start();

        // 9 秒缓慢推镜，画面不呆板
        ivPhoto.animate()
                .scaleX(1.05f)
                .scaleY(1.05f)
                .setDuration(9000)
                .setInterpolator(new LinearInterpolator())
                .start();
    }

    /** 洗牌袋：一轮内不重复；新一轮首张避开上一张 */
    private int nextIndex() {
        if (bag.isEmpty()) {
            for (int i = 0; i < PHOTOS.length; i++) {
                bag.add(i);
            }
            Collections.shuffle(bag, random);
            if (bag.size() > 1 && bag.get(0) == current) {
                Collections.swap(bag, 0, bag.size() - 1);
            }
        }
        return bag.remove(0);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
