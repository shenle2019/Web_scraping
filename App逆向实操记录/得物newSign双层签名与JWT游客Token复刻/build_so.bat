@echo off
set NDK=D:\ndk\android-ndk-r26d
set PROJ=%~dp0android
set OUT=%PROJ%\app\src\main\jniLibs\arm64-v8a
if not exist "%OUT%" mkdir "%OUT%"
"%NDK%\toolchains\llvm\prebuilt\windows-x86_64\bin\aarch64-linux-android24-clang.cmd" -shared -fPIC -O2 -o "%OUT%\libJNIEncrypt.so" "%PROJ%\app\src\main\jni\aes_jni.c"
echo BUILD_SO_EXIT=%ERRORLEVEL%
dir "%OUT%\libJNIEncrypt.so"
