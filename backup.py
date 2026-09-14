"""Back up the board editor's shared boards and sheets from Firestore.

  python3 backup.py

Reads every board and sheet through Firestore's REST API (the database's
rules allow reading) and writes them under backups/: each board as the
editor's own .json (drop one into boards/ or import it in the editor to
restore it), each sheet as its PNG beside a small .json of its cells.
The GitHub Actions job in .github/workflows/board-backup.yml (on the site
repository) runs this every four hours and commits whatever changed.
"""
import base64, json, os, re, sys, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "backups")
cfg_text = open(os.path.join(ROOT, "firebase-config.js")).read()
PROJECT = re.search(r'projectId:\s*"([^"]+)"', cfg_text).group(1)
KEY = re.search(r'apiKey:\s*"([^"]+)"', cfg_text).group(1)
BASE = "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents" % PROJECT


def value(v):
    """One Firestore REST value to plain Python."""
    if "stringValue" in v: return v["stringValue"]
    if "integerValue" in v: return int(v["integerValue"])
    if "doubleValue" in v: return v["doubleValue"]
    if "booleanValue" in v: return v["booleanValue"]
    if "nullValue" in v: return None
    if "mapValue" in v: return {k: value(x) for k, x in v["mapValue"].get("fields", {}).items()}
    if "arrayValue" in v: return [value(x) for x in v["arrayValue"].get("values", [])]
    if "timestampValue" in v: return v["timestampValue"]
    return None


def docs(path):
    out, token = [], None
    while True:
        q = {"pageSize": 300, "key": KEY}
        if token: q["pageToken"] = token
        with urllib.request.urlopen("%s/%s?%s" % (BASE, path, urllib.parse.urlencode(q))) as r:
            page = json.load(r)
        for d in page.get("documents", []):
            out.append((d["name"].rsplit("/", 1)[1], {k: value(v) for k, v in d.get("fields", {}).items()}))
        token = page.get("nextPageToken")
        if not token:
            return out


def safe(name):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "unnamed"


boards = docs("boards")
os.makedirs(os.path.join(OUT, "boards"), exist_ok=True)
for bid, b in boards:
    b.pop("lock", None)
    with open(os.path.join(OUT, "boards", "%s.json" % safe(bid)), "w") as f:
        json.dump(b, f, separators=(",", ":"))
sheets = docs("sheets")
os.makedirs(os.path.join(OUT, "sheets"), exist_ok=True)
for sid, s in sheets:
    chunks = sorted(docs("sheets/%s/chunks" % sid), key=lambda c: c[1].get("n", 0))
    png = "".join(c[1].get("data", "") for c in chunks)
    stem = "%s_%s" % (sid, safe(s.get("name", "sheet")))
    if png:
        with open(os.path.join(OUT, "sheets", stem + ".png"), "wb") as f:
            f.write(base64.b64decode(png))
    if isinstance(s.get("tiles"), list):  # stored as "x,y" strings (no nested arrays in Firestore)
        s["tiles"] = [[int(a) for a in t.split(",")] if isinstance(t, str) else t for t in s["tiles"]]
    with open(os.path.join(OUT, "sheets", stem + ".json"), "w") as f:
        json.dump({k: v for k, v in s.items()}, f, separators=(",", ":"))
print("backed up %d boards and %d sheets into backups/" % (len(boards), len(sheets)))
