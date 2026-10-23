#!/system/bin/sh
# 复刻课件 4.3 节：删除识货 7.20.1 的 libmsaoaidsec.so（反调试检测 so），保留其他业务 so。
# 仅对本机已安装的旧版本 com.hupu.shihuo 生效，用于学习验证；卸载重装即恢复。
PKG=com.hupu.shihuo
BASE=$(pm path $PKG | head -1 | sed 's/^package://; s#/base.apk$##')
LIB="$BASE/lib/arm64/libmsaoaidsec.so"
echo "BASE=$BASE"
echo "before:"
ls -l "$LIB"
rm -f "$LIB"
if [ -f "$LIB" ]; then echo "STILL_EXISTS"; else echo "REMOVED $LIB"; fi
