"""Fetch the development repositories named in repair/vendor/MANIFEST.json.   python repair/fetch.py

Each is a source archive from PyPI, pinned by SHA-256.  An archive already present is checked, not fetched again.
Archives are unpacked into repair/repos/<name>/ with tarfile's 'data' filter (no links out of the tree, no devices).
Neither the archives nor the unpacked trees are committed."""
import hashlib, json, os, shutil, tarfile, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(HERE, "vendor"); R = os.path.join(HERE, "repos")
for m in json.load(open(os.path.join(V, "MANIFEST.json"))):
    path = os.path.join(V, m["file"])
    if not os.path.exists(path): open(path, "wb").write(urllib.request.urlopen(m["url"], timeout=60).read())
    h = hashlib.sha256(open(path, "rb").read()).hexdigest(); assert h == m["sha256"], f"{m['file']}: digest {h} is not the pinned one"
    dest = os.path.join(R, m["name"]); shutil.rmtree(dest, ignore_errors=True); tmp = dest + ".tmp"; shutil.rmtree(tmp, ignore_errors=True)
    with tarfile.open(path) as t: t.extractall(tmp, filter="data")
    top = os.listdir(tmp); assert len(top) == 1, top; os.rename(os.path.join(tmp, top[0]), dest); os.rmdir(tmp)
    print(f"{m['name']} {m['version']}  {m['bytes']} bytes  sha256 {h[:16]}…  -> repair/repos/{m['name']}")
