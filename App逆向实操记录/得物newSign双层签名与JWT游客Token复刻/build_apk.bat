@echo off
set JAVA_HOME=D:\Android\jbr
set GRADLE=C:\Users\Administrator\.gradle\wrapper\dists\gradle-8.0-bin\ca5e32bp14vu59qr306oxotwh\gradle-8.0\bin\gradle.bat
cd /d "%~dp0android"
call "%GRADLE%" --offline assembleDebug > "%~dp0build_apk.log" 2>&1
echo GRADLE_EXIT=%ERRORLEVEL%
dir /b "%~dp0android\app\build\outputs\apk\debug"
