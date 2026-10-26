import zipfile
apk = r"E:\路飞学城\课件\APP逆向(12期)\day17-B站播放量01\软件\B站-v6240.apk"
z = zipfile.ZipFile(apk)
so = [n for n in z.namelist() if n.endswith("libbili.so")]
print("libbili.so entries:", so)
for name in so:
    data = z.read(name)
    for needle in [b"560c52cc", b"d288fed0", b"45859ed1", b"8bffd973"]:
        print("  %-10s %s  (%s)" % (needle.decode(), needle in data, name))
