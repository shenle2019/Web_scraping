#!/system/bin/sh
# 复刻课件 4.3 节：从 /data/app/<pkg>/lib/arm64 删除检测 so，让 System.loadLibrary 失败。
# 只删除本机自建 App com.repl.shihuo 的 libfridadetector.so，不动任何第三方应用。
PKG=com.repl.shihuo
BASE=$(pm path $PKG | head -1 | sed 's/^package://; s#/base.apk$##')
LIB="$BASE/lib/arm64/libfridadetector.so"
echo "BASE=$BASE"
echo "before:"
ls -l "$LIB"
rm -f "$LIB"
echo "after:"
if [ -f "$LIB" ]; then echo "STILL_EXISTS"; else echo "REMOVED $LIB"; fi
ls "$BASE/lib/arm64/"
