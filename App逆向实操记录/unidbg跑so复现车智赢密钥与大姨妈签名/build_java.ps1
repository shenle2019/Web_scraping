# 仅限学习研究，禁止商用。
# 用法：在 unidbg-0.9.7 目录执行  .\build_java.ps1
# 依赖：JDK 1.8（javac/java/jar）+ 课件自带的 out\artifacts\unidbg_0_9_7_jar\unidbg-0.9.7.jar

$ErrorActionPreference = "Stop"
$jdk = "C:\Program Files\Java\jdk-1.8\bin"
$jar = "out\artifacts\unidbg_0_9_7_jar\unidbg-0.9.7.jar"

if (-not (Test-Path $jar)) { throw "缺少 $jar，请先从课件 rar 中抽取" }

New-Item -ItemType Directory -Force -Path classes | Out-Null
& "$jdk\javac.exe" -encoding UTF-8 -cp $jar -d classes src\CheSignDemo.java src\DymSignDemo.java
& "$jdk\jar.exe" cfm che-sign.jar manifest.txt -C classes .
Write-Host "构建完成：che-sign.jar"
