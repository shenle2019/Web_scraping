# 不依赖 Gradle 的构建脚本：aapt2 -> javac -> d8 -> NDK clang -> 打包 -> 对齐 -> 签名
param(
    [string]$Sdk = "C:\Users\Administrator\AppData\Local\Android\Sdk",
    [string]$Ndk = "D:\soft\android-ndk-r25c",
    [string]$JavaHome = "C:\Program Files\Java\jdk-1.8",
    [switch]$SkipNative
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Bt = Join-Path $Sdk "build-tools\30.0.3"
$Jar = Join-Path $Sdk "platforms\android-30\android.jar"
$Out = Join-Path $Root "build"
$env:JAVA_HOME = $JavaHome
$env:PATH = (Join-Path $JavaHome "bin") + ";" + $env:PATH

Write-Host "[1/7] 清理 build/"
Remove-Item $Out -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force (Join-Path $Out "classes") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $Out "lib\arm64-v8a") | Out-Null

if (-not $SkipNative) {
    Write-Host "[2/7] 编译 native 库 libbili.so (arm64-v8a)"
    $Cc = Join-Path $Ndk "toolchains\llvm\prebuilt\windows-x86_64\bin\aarch64-linux-android21-clang.cmd"
    if (-not (Test-Path $Cc)) { throw "找不到 NDK clang: $Cc" }
    & $Cc -shared -fPIC -O2 -fvisibility=default `
        -o (Join-Path $Out "lib\arm64-v8a\libbili.so") `
        (Join-Path $Root "app\jni\bili_sign.c")
    if ($LASTEXITCODE -ne 0) { throw "native 编译失败" }
} else {
    Write-Host "[2/7] 跳过 native 编译（复用 build/lib）"
}

Write-Host "[3/7] aapt2 link 生成壳 APK"
& (Join-Path $Bt "aapt2.exe") link -o (Join-Path $Out "base.apk") `
    -I $Jar --manifest (Join-Path $Root "app\AndroidManifest.xml") `
    --min-sdk-version 21 --target-sdk-version 30 `
    --version-code 1 --version-name 1.0
if ($LASTEXITCODE -ne 0) { throw "aapt2 link 失败" }

Write-Host "[4/7] javac 编译 Java 源码"
$Sources = Get-ChildItem (Join-Path $Root "app\src") -Recurse -Filter *.java | ForEach-Object { $_.FullName }
& (Join-Path $JavaHome "bin\javac.exe") -encoding UTF-8 -source 1.8 -target 1.8 -nowarn `
    -bootclasspath $Jar -d (Join-Path $Out "classes") $Sources
if ($LASTEXITCODE -ne 0) { throw "javac 失败" }

Write-Host "[5/7] d8 生成 classes.dex"
$Classes = Get-ChildItem (Join-Path $Out "classes") -Recurse -Filter *.class | ForEach-Object { $_.FullName }
New-Item -ItemType Directory -Force (Join-Path $Out "dexout") | Out-Null
# 直接用 java -cp d8.jar 调用，避开 d8.bat 在中文路径下的参数传递问题
& (Join-Path $JavaHome "bin\java.exe") -cp (Join-Path $Bt "lib\d8.jar") `
    com.android.tools.r8.D8 --lib $Jar --min-api 21 --output (Join-Path $Out "dexout") $Classes
if ($LASTEXITCODE -ne 0) { throw "d8 失败" }

Write-Host "[6/7] 打包 dex + so 并 zipalign"
python (Join-Path $Root "pack_apk.py") (Join-Path $Out "base.apk") `
    (Join-Path $Out "dexout\classes.dex") (Join-Path $Out "lib") (Join-Path $Out "unsigned.apk")
if ($LASTEXITCODE -ne 0) { throw "打包失败" }
& (Join-Path $Bt "zipalign.exe") -f 4 (Join-Path $Out "unsigned.apk") (Join-Path $Out "aligned.apk")
if ($LASTEXITCODE -ne 0) { throw "zipalign 失败" }

Write-Host "[7/7] apksigner 签名"
$Ks = Join-Path $env:USERPROFILE ".android\debug.keystore"
if (-not (Test-Path $Ks)) {
    & (Join-Path $JavaHome "bin\keytool.exe") -genkeypair -keystore $Ks -storepass android -keypass android `
        -alias androiddebugkey -dname "CN=Android Debug,O=Android,C=US" `
        -keyalg RSA -keysize 2048 -validity 10000
}
& (Join-Path $Bt "apksigner.bat") sign --ks $Ks --ks-pass pass:android --key-pass pass:android `
    --ks-key-alias androiddebugkey --out (Join-Path $Out "BiliReplica.apk") (Join-Path $Out "aligned.apk")
if ($LASTEXITCODE -ne 0) { throw "签名失败" }

Write-Host "构建完成: $(Join-Path $Out 'BiliReplica.apk')"
