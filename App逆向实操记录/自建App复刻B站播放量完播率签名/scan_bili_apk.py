import zipfile, sys
apk = r"E:\路飞学城\课件\APP逆向(12期)\day17-B站播放量01\软件\B站-v6240.apk"
needles = [b"x/report/click/android2", b"x/report/heartbeat/mobile", b"9cafa6466a028bfb",
           b"fd6b639dbcff0c2a1b03b389ec763c4b", b"77b07a672d57d64c", b"libbili.so",
           b"560c52cc", b"fp_local"]
z = zipfile.ZipFile(apk)
names = [n for n in z.namelist() if n.endswith(".dex") or n.endswith(".so")]
print("entries:", len(names), "dex/so:", len(names))
hits = {n: [] for n in needles}
for name in names:
    if not (name.endswith(".dex")):
        continue
    data = z.read(name)
    for n in needles:
        if n in data:
            hits[n].append(name)
for n, where in hits.items():
    print("%-40s %s" % (n.decode(), "FOUND in " + ",".join(where) if where else "not in dex"))
