package com.shenjiahang.babyalbum;

import android.os.Bundle;
import android.view.View;
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
/* loaded from: classes3.dex */
public class MainActivity extends AppCompatActivity {
    private static final int[] PHOTOS = {R.drawable.photo_01, R.drawable.photo_02, R.drawable.photo_03, R.drawable.photo_04, R.drawable.photo_05, R.drawable.photo_06, R.drawable.photo_07, R.drawable.photo_08, R.drawable.photo_09, R.drawable.photo_10, R.drawable.photo_11};
    private Button btnNext;
    private MaterialCardView cardPhoto;
    private ImageView ivPhoto;
    private TextView tvChip;
    private final Random random = new Random();
    private final List<Integer> bag = new ArrayList();
    private int current = -1;
    private boolean switching = false;

    /* JADX INFO: Access modifiers changed from: protected */
    @Override // androidx.fragment.app.FragmentActivity, androidx.activity.ComponentActivity, androidx.core.app.ComponentActivity, android.app.Activity
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        this.cardPhoto = (MaterialCardView) findViewById(R.id.cardPhoto);
        this.ivPhoto = (ImageView) findViewById(R.id.ivPhoto);
        this.tvChip = (TextView) findViewById(R.id.tvChip);
        this.btnNext = (Button) findViewById(R.id.btnNext);
        int nextIndex = nextIndex();
        this.current = nextIndex;
        applyPhoto(nextIndex);
        this.cardPhoto.setAlpha(0.0f);
        this.cardPhoto.setTranslationY(dp(22));
        this.cardPhoto.animate().alpha(1.0f).translationY(0.0f).setDuration(520L).setInterpolator(new DecelerateInterpolator()).start();
        this.btnNext.setOnClickListener(new View.OnClickListener() { // from class: com.shenjiahang.babyalbum.MainActivity$$ExternalSyntheticLambda2
            @Override // android.view.View.OnClickListener
            public final void onClick(View view) {
                MainActivity.this.m30lambda$onCreate$1$comshenjiahangbabyalbumMainActivity(view);
            }
        });
        this.cardPhoto.setOnClickListener(new View.OnClickListener() { // from class: com.shenjiahang.babyalbum.MainActivity$$ExternalSyntheticLambda3
            @Override // android.view.View.OnClickListener
            public final void onClick(View view) {
                MainActivity.this.m31lambda$onCreate$2$comshenjiahangbabyalbumMainActivity(view);
            }
        });
    }

    /* JADX INFO: Access modifiers changed from: package-private */
    /* renamed from: lambda$onCreate$1$com-shenjiahang-babyalbum-MainActivity  reason: not valid java name */
    public /* synthetic */ void m30lambda$onCreate$1$comshenjiahangbabyalbumMainActivity(final View v) {
        v.performHapticFeedback(1);
        v.animate().scaleX(0.96f).scaleY(0.96f).setDuration(70L).withEndAction(new Runnable() { // from class: com.shenjiahang.babyalbum.MainActivity$$ExternalSyntheticLambda0
            @Override // java.lang.Runnable
            public final void run() {
                v.animate().scaleX(1.0f).scaleY(1.0f).setDuration(150L).start();
            }
        }).start();
        showNext();
    }

    /* JADX INFO: Access modifiers changed from: package-private */
    /* renamed from: lambda$onCreate$2$com-shenjiahang-babyalbum-MainActivity  reason: not valid java name */
    public /* synthetic */ void m31lambda$onCreate$2$comshenjiahangbabyalbumMainActivity(View v) {
        showNext();
    }

    private void showNext() {
        if (this.switching) {
            return;
        }
        this.switching = true;
        this.cardPhoto.animate().alpha(0.0f).scaleX(0.97f).scaleY(0.97f).setDuration(120L).withEndAction(new Runnable() { // from class: com.shenjiahang.babyalbum.MainActivity$$ExternalSyntheticLambda4
            @Override // java.lang.Runnable
            public final void run() {
                MainActivity.this.m33lambda$showNext$4$comshenjiahangbabyalbumMainActivity();
            }
        }).start();
    }

    /* JADX INFO: Access modifiers changed from: package-private */
    /* renamed from: lambda$showNext$4$com-shenjiahang-babyalbum-MainActivity  reason: not valid java name */
    public /* synthetic */ void m33lambda$showNext$4$comshenjiahangbabyalbumMainActivity() {
        int nextIndex = nextIndex();
        this.current = nextIndex;
        applyPhoto(nextIndex);
        this.cardPhoto.animate().alpha(1.0f).scaleX(1.0f).scaleY(1.0f).setDuration(260L).setInterpolator(new DecelerateInterpolator()).withEndAction(new Runnable() { // from class: com.shenjiahang.babyalbum.MainActivity$$ExternalSyntheticLambda1
            @Override // java.lang.Runnable
            public final void run() {
                MainActivity.this.m32lambda$showNext$3$comshenjiahangbabyalbumMainActivity();
            }
        }).start();
    }

    /* JADX INFO: Access modifiers changed from: package-private */
    /* renamed from: lambda$showNext$3$com-shenjiahang-babyalbum-MainActivity  reason: not valid java name */
    public /* synthetic */ void m32lambda$showNext$3$comshenjiahangbabyalbumMainActivity() {
        this.switching = false;
    }

    private void applyPhoto(int index) {
        this.ivPhoto.animate().cancel();
        this.ivPhoto.setScaleX(1.0f);
        this.ivPhoto.setScaleY(1.0f);
        ImageView imageView = this.ivPhoto;
        int[] iArr = PHOTOS;
        imageView.setImageResource(iArr[index]);
        this.ivPhoto.setContentDescription(getString(R.string.photo_desc, new Object[]{Integer.valueOf(index + 1)}));
        this.tvChip.setText(getString(R.string.chip_format, new Object[]{Integer.valueOf(index + 1), Integer.valueOf(iArr.length)}));
        this.tvChip.setScaleX(0.9f);
        this.tvChip.setScaleY(0.9f);
        this.tvChip.animate().scaleX(1.0f).scaleY(1.0f).setDuration(220L).start();
        this.ivPhoto.animate().scaleX(1.05f).scaleY(1.05f).setDuration(9000L).setInterpolator(new LinearInterpolator()).start();
    }

    private int nextIndex() {
        if (this.bag.isEmpty()) {
            for (int i = 0; i < PHOTOS.length; i++) {
                this.bag.add(Integer.valueOf(i));
            }
            Collections.shuffle(this.bag, this.random);
            if (this.bag.size() > 1 && this.bag.get(0).intValue() == this.current) {
                List<Integer> list = this.bag;
                Collections.swap(list, 0, list.size() - 1);
            }
        }
        return this.bag.remove(0).intValue();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
