"""Data loading with sha256 recording.  DATA ONLY from the two third-party repos."""
import hashlib, json, os
TMP = os.environ.get("TMPDIR", "/tmp")
CREILLY = os.path.join(TMP, "creilly")
WWAFA = os.path.join(TMP, "wwafa")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def records():
    return json.load(open(os.path.join(CREILLY, "data/records.json")))


def keys():
    K = json.load(open(os.path.join(CREILLY, "data/keys.json")))
    return {k["id"]: k for k in K}


def by_id():
    return {r["id"]: r for r in records()}
