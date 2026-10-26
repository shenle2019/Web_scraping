# 把 classes.dex 与 lib/ 原生库塞进 aapt2 产出的空壳 APK（避免依赖 Gradle）
import os
import sys
import zipfile

base_apk, dex, libdir, out_apk = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

with zipfile.ZipFile(base_apk, "r") as src:
    entries = [(i, src.read(i.filename)) for i in src.infolist()]

with zipfile.ZipFile(out_apk, "w", zipfile.ZIP_DEFLATED) as dst:
    for info, data in entries:
        dst.writestr(info, data)
    dst.write(dex, "classes.dex")
    for root, _, files in os.walk(libdir):
        for name in files:
            path = os.path.join(root, name)
            rel = os.path.relpath(path, libdir).replace(os.sep, "/")
            dst.write(path, "lib/" + rel)

print("packed ->", out_apk, os.path.getsize(out_apk), "bytes")
