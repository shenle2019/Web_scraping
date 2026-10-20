# jadx 反编译与源码对照

输入：最终版 `app-debug.apk`（MD5 `5C3905661145E59C1682745803792848`）
输出：739 个类，`com.shenjiahang.babyalbum.MainActivity` 共 142 行（与源码行数一致）
完整产物：`evidence/jadx_MainActivity.java`

## 1. 多 dex 标注

反编译结果类头多了一行注释：

```java
/* loaded from: classes3.dex */
public class MainActivity extends AppCompatActivity {
```

源码没有这一行。debug 包被拆成多个 dex（classes.dex / classes2.dex / classes3.dex），jadx 用它标明这个类来自哪个 dex。release 包开启 minify 后 dex 分配还会变化，不能把 `classes3` 当成固定事实。

## 2. lambda 脱糖

源码：

```java
btnNext.setOnClickListener(v -> {
    v.performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY);
    ...
    showNext();
});
```

反编译：

```java
this.btnNext.setOnClickListener(new View.OnClickListener() { // from class: ...MainActivity$$ExternalSyntheticLambda2
    @Override
    public final void onClick(View view) {
        MainActivity.this.m30lambda$onCreate$1$comshenjiahangbabyalbumMainActivity(view);
    }
});
```

要点：

- `$$ExternalSyntheticLambdaN` 是 D8 脱糖生成的合成类，不是源码里写的；
- 合成方法名把包名里的点替换成下划线：`m30lambda$onCreate$1$comshenjiahangbabyalbumMainActivity`；
- 方法编号（`m30`、`m31`、`m32`、`m33`）由编译器分配，重新编译可能变化，不能作为稳定锚点。

## 3. 常量内联

| 源码 | 反编译 |
| --- | --- |
| `HapticFeedbackConstants.VIRTUAL_KEY` | `performHapticFeedback(1)` |
| `520`（入场动画时长） | `setDuration(520L)` |
| `9000`（Ken Burns 时长） | `setDuration(9000L)` |

常量在编译期被折叠成立即数，反编译看不到原来的常量名。逆向时遇到“魔法数字”，要结合上下文和 Android API 常量表还原语义。

## 4. 可变参数

源码：

```java
getString(R.string.photo_desc, index + 1)
```

反编译：

```java
getString(R.string.photo_desc, new Object[]{Integer.valueOf(index + 1)})
```

`getString(int, Object...)` 的可变参数被展开成显式数组，同时触发自动装箱。看到 `new Object[]{Integer.valueOf(...)}` 就是可变参数调用的典型特征。

## 5. 泛型擦除

源码：

```java
private final List<Integer> bag = new ArrayList<>();
```

反编译：

```java
private final List<Integer> bag = new ArrayList();
```

字段声明保留了泛型（来自 Signature 属性），但构造调用处的类型参数被擦除。取值时也因此多出 `((Integer) this.bag.remove(0)).intValue()`。

## 6. 非法 Java 标识符被重命名

```java
/* renamed from: lambda$onCreate$1$com-shenjiahang-babyalbum-MainActivity  reason: not valid java name */
public /* synthetic */ void m30lambda$onCreate$1$comshenjiahangbabyalbumMainActivity(final View v) {
```

D8 生成的合成方法名里带 `-`（来自包名），不是合法 Java 标识符；jadx 把它替换成下划线并保留原始名字注释。这条注释是判断“该方法是编译器生成”的可靠线索。

## 7. 继承链注解被展开

```java
@Override // androidx.fragment.app.FragmentActivity, androidx.activity.ComponentActivity, androidx.core.app.ComponentActivity, android.app.Activity
public void onCreate(Bundle savedInstanceState) {
```

源码中 `MainActivity extends AppCompatActivity`，javadoc 只写 `@Override`。jadx 把整条继承链上被重写的方法都列在注解里，反而更方便确认类层级：`AppCompatActivity` → `FragmentActivity` → `ComponentActivity` → `Activity`。

## 8. 其他细节

- 访问修饰符补全：源码省略的 `private` 字段、包级可见的合成方法，反编译都会显式写出；
- `this.` 前缀：所有字段访问被写成 `this.xxx`，源码里通常省略；
- 强制转换：`findViewById` 的返回值补上 `(MaterialCardView)`、`(ImageView)` 等强转，源码里由泛型推断省略；
- 局部变量名丢失：源码的 `nextIndex` 等名字在反编译里可能变成 `nextIndex` 或 `iArr`，取决于 LocalVariableTable 是否保留。debug 包保留了大部分名字，release 包混淆后会全部丢失。

## 9. 逆向启示

1. 看到 `$$ExternalSyntheticLambda`、`mNNlambda$` 不要当成业务逻辑，回到源码的 lambda 位置理解；
2. 常量内联会让“找 520/9000”这类搜索失效，优先按调用链定位；
3. `loaded from: classesN.dex` 可用于判断多 dex 结构，但不能当成版本指纹；
4. 自己的 App 反编译对照，是理解脱糖、内联、擦除最快的方式——代码是已知的，差异一目了然。
