"""Regenerate the true ciphertext of each calibration entry by re-encrypting creilly's
plaintext under its key with comp-adfgvx's engine (search/adfgvx/engine.py, read-only import).

usage: calib_truth.py REPO OUT.json
'*' = a symbol the truth cannot fix (an unknown plaintext character, or the unpaired last
symbol of an odd-length message, which the plaintext does not determine).
Sanity check, printed as counts only: the truth against creilly's `ciphertext` field.
"""
import json, sys, os
repo, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(repo, "search", "adfgvx"))
import engine

recs = {r["id"]: r for r in json.load(open(os.path.join(repo, "ciphertexts/adfgvx-1918-log.records.json")))}
keys = {k["id"]: k for k in json.load(open(os.path.join(repo, "ciphertexts/adfgvx-1918-log.keys.json")))}
wl = json.load(open(os.path.join(repo, "ciphertexts/adfgvx-1918-scan-worklist.json")))
res = {}
for e in wl["calibration"]:
    r = recs[e["id"]]; k = keys[r["key"]]
    pt = "".join(c if c in k["square"] and c != "?" else "?" for c in r["plaintext"])
    ct = engine.encrypt(pt, k["square"], k["transposition"])
    ct = ct.replace("?", "*")
    cr = engine.clean(r["ciphertext"]) if r["ciphertext"] else ""
    if len(cr) == len(ct) + 1:          # odd length: the last symbol is unpaired
        # engine.transpose of an even interim; the unpaired symbol sits in some column. Rebuild
        # by encrypting with a wildcard pad and dropping its pair partner.
        pad = engine.transpose(engine.substitute(pt, k["square"]) + "*", k["transposition"])
        ct = pad
    agree = sum(1 for a, b in zip(ct, cr) if a == b)
    known = sum(1 for a, b in zip(ct, cr) if a != "*" and b not in "-?")
    res[e["id"]] = {"truth": ct, "key": r["key"], "len_truth": len(ct), "len_creilly_ct": len(cr),
                    "agree_with_creilly_ct": agree, "comparable": known}
    print(e["id"], r["key"], len(ct), len(cr), "agree", agree, "of", known)
json.dump(res, open(out, "w"), indent=1)
