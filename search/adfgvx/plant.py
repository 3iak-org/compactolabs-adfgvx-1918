"""Planted-control generator for ADFGVX (comp-adfgvx, 2026-10-31).

A control is a ciphertext made from a known plaintext under a known key, with known mutilations,
so that an attack's recovery rate and false-positive rate can be measured.  Every control carries
its full truth record (plaintext, key, the exact edit log), so a check can re-create it.

    python -I search/adfgvx/plant.py --n 5 --seed 1 --width 20 --len 176 --edits census \
        --e5-rate 0.0066 --out $TMPDIR/controls.jsonl

--len      target CIPHERTEXT length before mutilation (even; plaintext = len/2 characters)
--width    transposition width k (random key), or --key <id> for a key from keys.json
--edits    'census'  : draw one solved message's event profile (types and run lengths) from
                       results/adfgvx-mutilation.csv, uniformly over messages, at random positions
           'none'    : no edits
           'E1:2,E5:1,E3:1,...' : exactly these events (E1/E2 accept E1x3 = a run of 3)
--e5-rate  extra wrong-symbol rate per symbol (Poisson), e.g. the repeated-reception estimate,
           because the census itself cannot see E5 in class A messages
--source   'corpus' (default): plaintext drawn from the solved entries' plaintexts, skipping any
           with unknown marks and any id in --exclude; or a path to a text file (one plaintext
           per line, characters A-Z0-9)
"""
import argparse
import csv
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
from engine import substitute, transpose, LAB  # noqa: E402

ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def random_key(rng, k):
    sq = list(ALPH)
    rng.shuffle(sq)
    t = list(range(1, k + 1))
    rng.shuffle(t)
    return "".join(sq), t


def corpus_plaintexts(exclude=()):
    rec = json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.records.json")))
    out = []
    for e in rec:
        p = e["plaintext"]
        if not p or not e["status"].startswith("Solved") or e["id"] in exclude:
            continue
        if any(c not in ALPH for c in p):
            continue
        out.append((e["id"], p))
    return out


def take_plaintext(rng, pool, n_chars):
    """Concatenate randomly chosen corpus plaintexts (separated by nothing) and cut a window."""
    buf, ids = "", []
    while len(buf) < n_chars:
        i, p = rng.choice(pool)
        buf += p
        ids.append(i)
    return buf[:n_chars], ids


def census_profiles(path=None):
    path = path or os.path.join(ROOT, "results", "adfgvx-mutilation.csv")
    rows = list(csv.DictReader(l for l in open(path) if not l.startswith("#")))
    prof = []
    for r in rows:
        evs = []
        for tok in (r["edit_script"] or "").split():
            k, rest = tok.split(":", 1)
            ty = rest.split("@")[0]
            L = int("".join(c for c in ty if c.isdigit()))
            if k in ("E1", "E2", "E3", "E4", "E5"):
                evs.append((k, L, ty.rstrip("0123456789")))
        prof.append((r["id"], evs))
    return prof


def parse_edits(spec):
    evs = []
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        k, c = tok.split(":")
        L = 1
        if "x" in k:
            k, L = k.split("x")
            L = int(L)
        for _ in range(int(c)):
            evs.append((k, L, None))
    return evs


def poisson(rng, lam):
    if lam <= 0:
        return 0
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def mutilate(rng, ct, events):
    """Apply events at random positions; returns (new ct, log). E3: whole 5-group drop or
    duplicate at a group boundary. Positions refer to the string at the time of the edit."""
    c = list(ct)
    log = []
    for k, L, how in events:
        n = len(c)
        if k == "E1" or (k == "E3" and (how == "del" or (how is None and rng.random() < 0.5))):
            if k == "E3":
                L = max(5, L - L % 5)
                p = 5 * rng.randrange(max(1, (n - L) // 5 + 1))
            else:
                p = rng.randrange(max(1, n - L + 1))
            log.append({"type": k, "op": "del", "pos": p, "len": L, "removed": "".join(c[p:p + L])})
            del c[p:p + L]
        elif k in ("E2", "E3"):
            if k == "E3":
                L = max(5, L - L % 5)
                p = 5 * rng.randrange(max(1, n // 5))
                ins = c[p:p + L] if rng.random() < 0.5 else [rng.choice(LAB) for _ in range(L)]
                q = p + L
            else:
                q = rng.randrange(n + 1)
                ins = [rng.choice(LAB) for _ in range(L)]
            log.append({"type": k, "op": "ins", "pos": q, "len": L, "inserted": "".join(ins)})
            c[q:q] = ins
        elif k == "E4":
            p = rng.randrange(n)
            log.append({"type": "E4", "op": "lost", "pos": p, "was": c[p]})
            c[p] = "-"
        elif k == "E5":
            p = rng.randrange(n)
            new = rng.choice([s for s in LAB if s != c[p]])
            log.append({"type": "E5", "op": "sub", "pos": p, "was": c[p], "now": new})
            c[p] = new
        else:
            raise ValueError(k)
    return "".join(c), log


def make_control(rng, length, width=None, key=None, events=(), e5_rate=0.0, e6=0, pool=None,
                 source_ids=None):
    if key is None:
        sq, tr = random_key(rng, width)
        key = {"id": "random", "square": sq, "transposition": tr}
    pt, ids = take_plaintext(rng, pool, length // 2)
    interim = substitute(pt, key["square"])
    e6log = []
    for _ in range(e6):
        p = rng.randrange(len(interim) + 1)
        s = rng.choice(LAB)
        e6log.append({"type": "E6", "op": "interim_ins", "pos": p, "inserted": s})
        interim = interim[:p] + s + interim[p:]
    true_ct = transpose(interim, key["transposition"])
    evs = list(events)
    n5 = poisson(rng, e5_rate * len(true_ct))
    evs += [("E5", 1, None)] * n5
    rng.shuffle(evs)
    ct, log = mutilate(rng, true_ct, evs)
    return {"plaintext": pt, "plaintext_from": ids, "key": key, "true_ct": true_ct,
            "ciphertext": ct, "edits": e6log + log, "n_extra_e5": n5}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--len", type=int, required=True)
    ap.add_argument("--width", type=int)
    ap.add_argument("--key")
    ap.add_argument("--edits", default="none")
    ap.add_argument("--e5-rate", type=float, default=0.0)
    ap.add_argument("--e6", type=int, default=0)
    ap.add_argument("--exclude", default="")
    ap.add_argument("--source", default="corpus")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    excl = set(x for x in a.exclude.split(",") if x)
    if a.source == "corpus":
        pool = corpus_plaintexts(excl)
    else:
        pool = [(f"line{i}", l.strip()) for i, l in enumerate(open(a.source)) if l.strip()]
    key = None
    if a.key:
        keys = {k["id"]: k for k in json.load(open(os.path.join(ROOT, "ciphertexts",
                                                                "adfgvx-1918-log.keys.json")))}
        key = keys[a.key]
        if "?" in key["square"]:
            sys.exit("key has blank square cells; plaintext characters there cannot be encrypted")
    profiles = census_profiles() if a.edits == "census" else None
    with open(a.out, "w") as f:
        for i in range(a.n):
            if profiles:
                pid, evs = rng.choice(profiles)
                evs = [(k, L, how) for k, L, how in evs]
            else:
                pid, evs = None, (parse_edits(a.edits) if a.edits != "none" else [])
            c = make_control(rng, a.len, a.width, key, evs, a.e5_rate, a.e6, pool)
            c.update({"control": i, "seed": a.seed, "profile_from": pid,
                      "args": vars(a)})
            f.write(json.dumps(c) + "\n")


if __name__ == "__main__":
    main()
