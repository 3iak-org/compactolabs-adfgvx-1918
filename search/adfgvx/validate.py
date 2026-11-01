"""Validation of the engine and the census (comp-adfgvx, 2026-10-31).

    ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/validate.py

1. Engine: re-decrypt every census entry under its key (class A must read back exactly).
2. Corrupted input: for every class A entry, corrupt the log text (one substitution, one deletion,
   one insertion) or the key (two transposition columns swapped; the neighbouring period's key)
   and check that the census reports exactly the planted damage, and that the decryption fails.
3. Planted edits: random keys, corpus plaintexts, edits drawn from the census profiles plus extra
   E5 at the repeated-reception rate; compare the census's minimal cost with the planted count.
   This measures, under control, how far a minimal edit script undercounts true damage.
Output: results/adfgvx-census-validation.md
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
from engine import encrypt, decrypt, transpose, substitute, LAB  # noqa: E402
from align import align, events  # noqa: E402
from census import edcost_lib, method_class, in_census, quant  # noqa: E402
from plant import corpus_plaintexts, census_profiles, make_control  # noqa: E402
from provenance import header as prov_header  # noqa: E402

SEED = 20261031
E5_RATE = 0.0066   # per symbol: repeated-reception estimate, results/adfgvx-mutilation.tables.md s.10


def compatible(d, p):
    return len(d) == len(p) and all(a == b or b in "-?#_" or a in "-?" for a, b in zip(d, p))


def main():
    rec = json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.records.json")))
    keys = {k["id"]: k for k in json.load(open(os.path.join(ROOT, "ciphertexts",
                                                            "adfgvx-1918-log.keys.json")))}
    ed = edcost_lib()
    rng = random.Random(SEED)
    L = []
    W = L.append
    W("# ADFGVX 1918: validation of the engine and the census\n")
    W(prov_header("", "search/adfgvx/validate.py"))
    W(f"RNG seed {SEED}.\n")

    # 1 engine
    W("## 1. Engine: re-decrypting every census entry under its key\n")
    cen = [e for e in rec if in_census(e)]
    W("| class | entries | decrypt(log text) reads back the plaintext exactly | decrypt(page reading) does | neither (the census measures the gap) |")
    W("|---|---|---|---|---|")
    from collections import Counter
    c = Counter()
    for e in cen:
        k = keys[e["key"]]
        cl = method_class(e)
        d1 = decrypt(e["printed"], k["square"], k["transposition"])
        page = (e["ciphertext"] or "").replace(" ", "").replace("?", "-")
        d2 = decrypt(page, k["square"], k["transposition"])
        ok1 = compatible(d1, e["plaintext"])
        ok2 = compatible(d2, e["plaintext"])
        c[(cl, "n")] += 1
        c[(cl, "log")] += ok1
        c[(cl, "page")] += (ok2 and not ok1)
        c[(cl, "none")] += not (ok1 or ok2)
    for cl in sorted(set(k[0] for k in c)):
        W(f"| {cl} | {c[(cl,'n')]} | {c[(cl,'log')]} | {c[(cl,'page')]} | {c[(cl,'none')]} |")
    W("\n'Exactly' allows the plaintext's own unknown marks (`- ? # _`) and lost slots in the "
      "log. Class A entries that do not read back are the odd-length ones whose last symbol is "
      "an extra (census E2 = 1).\n")

    # 2 corrupted input
    W("## 2. Corrupted input: does the census see planted damage, and does the decryption fail?\n")
    A = [e for e in cen if method_class(e) == "A_as_transcribed"]
    tests = Counter()
    fails = []
    swapcosts = []
    wrongkey_fail = []
    order = ["sep19", "oct04", "oct28", "nov01", "nov04", "nov07", "nov10", "nov13_20",
             "nov13_16", "nov16", "nov19", "nov22", "nov25", "nov28"]
    for e in A:
        k = keys[e["key"]]
        sq, tr = k["square"], k["transposition"]
        T = encrypt(e["plaintext"], sq, tr)
        O = e["printed"]
        base = ed(T, O)
        letters = [i for i, ch in enumerate(O) if ch in LAB and i < len(T) and T[i] != "*"]
        p = rng.choice(letters)
        # substitution
        O1 = O[:p] + rng.choice([s for s in LAB if s != O[p]]) + O[p + 1:]
        c1 = ed(T, O1)
        tests["sub: census cost rises by exactly 1"] += (c1 == base + 1)
        d = decrypt(O1, sq, tr)
        dd = sum(1 for a, b in zip(d, decrypt(O, sq, tr)) if a != b)
        tests["sub: decryption changes in exactly 1 character"] += (dd == 1)
        # deletion
        O2 = O[:p] + O[p + 1:]
        c2 = ed(T, O2)
        tests["del: census cost rises by exactly 1"] += (c2 == base + 1)
        d = decrypt(O2, sq, tr)
        dd = sum(1 for a, b in zip(d, e["plaintext"]) if a != b and b not in "-?#_")
        tests["del: decryption no longer reads back (>=1 char wrong)"] += (dd >= 1)
        # insertion
        O3 = O[:p] + rng.choice(LAB) + O[p:]
        c3 = ed(T, O3)
        tests["ins: census cost rises by exactly 1"] += (c3 == base + 1)
        if c1 != base + 1 or c2 != base + 1 or c3 != base + 1:
            fails.append((e["id"], base, c1, c2, c3))
        # wrong key: swap two transposition columns
        tr2 = list(tr)
        i, j = rng.sample(range(len(tr2)), 2)
        tr2[i], tr2[j] = tr2[j], tr2[i]
        T2 = encrypt(e["plaintext"], sq, tr2)
        cs = ed(T2, O)
        tests["key (2 columns swapped): census cost > 0"] += (cs > 0)
        swapcosts.append(cs)
        # wrong key: EVERY other key of the 22 (keys.json), blank square cells -> wildcards
        for kid, kk in keys.items():
            if kid == e["key"]:
                continue
            T3 = encrypt(e["plaintext"], kk["square"], kk["transposition"])
            ok = ed(T3, O) >= len(O) // 4
            tests["key (each of the other 21 keys): census cost >= len/4"] += ok
            tests["key (each of the other 21 keys): tested"] += 1
            if not ok:
                wrongkey_fail.append((e["id"], kid, ed(T3, O), len(O)))
    W(f"Every one of the {len(A)} class A entries, one random position each:\n")
    W("| test | passed | of |")
    W("|---|---|---|")
    for t, v in tests.items():
        if t.endswith("tested"):
            continue
        n = tests["key (each of the other 21 keys): tested"] if "other 21" in t else len(A)
        W(f"| {t} | {v} | {n} |")
    W(f"\nPositions are drawn where the reference symbol is known (not a wildcard). Census cost "
      f"after swapping two transposition columns: median {quant(swapcosts,.5):g}, "
      f"min {min(swapcosts)}, p10 {quant(swapcosts,.1):g}. A swap of two adjacent-in-order "
      f"columns of similar content can cost little; it must never cost 0 unless the columns "
      f"are identical.\n")
    W(f"\nWrong-key pairs that did NOT cost >= len/4: {len(wrongkey_fail)}"
      + (": " + "; ".join(f"{a} under {b}: {c}/{d}" for a, b, c, d in wrongkey_fail[:20]) if wrongkey_fail else "")
      + ". Keys with many blank square cells turn plaintext letters into wildcards, which lowers "
        "the cost; the 22 keys are those of ciphertexts/adfgvx-1918-log.keys.json.\n")
    if fails:
        W("\nEntries where a single planted edit did not raise the cost by exactly 1 (an edit "
          "next to an existing one, or a substitution that recreates a neighbour, can be "
          "absorbed; this is the minimal-edit undercount in miniature):\n")
        for f in fails[:40]:
            W(f"- {f[0]}: base {f[1]}, after sub {f[2]}, del {f[3]}, ins {f[4]}")

    # 3 planted edits
    W("\n## 3. Planted edits: how far does the minimal edit script undercount?\n")
    pool = corpus_plaintexts()
    prof = census_profiles()
    lengths = [len(e["printed"]) - len(e["printed"]) % 2 for e in cen]
    N = 2000
    under = []
    rows = []
    for t in range(N):
        width = rng.randint(15, 23)
        Ln = rng.choice(lengths)
        pid, evs = rng.choice(prof)
        cnt = make_control(rng, Ln, width, None, evs, E5_RATE, 0, pool)
        planted_sym = sum(x.get("len", 1) for x in cnt["edits"] if x["type"] != "E4")
        planted_ev = sum(1 for x in cnt["edits"] if x["type"] != "E4")
        cost = ed(cnt["true_ct"], cnt["ciphertext"])
        under.append(planted_sym - cost)
        rows.append((planted_sym, planted_ev, cost))
    n_any = sum(1 for r in rows if r[0] > 0)
    eq = sum(1 for r in rows if r[0] > 0 and r[2] == r[0])
    lt = sum(1 for r in rows if r[2] < r[0])
    gt = sum(1 for r in rows if r[2] > r[0])
    W(f"{N} controls. Width uniform on 15..23; length drawn from the census lengths; event profile "
      f"drawn uniformly from the census rows (types and run lengths, random positions); extra E5 "
      f"Poisson at {E5_RATE} per symbol. E4 marks are not counted as edits (they are free).\n")
    W(f"- controls with any planted edit: {n_any}")
    W(f"- minimal cost = planted symbol edits: {eq} ({100*eq/max(n_any,1):.1f}%)")
    W(f"- minimal cost < planted (undercount): {lt} ({100*lt/max(n_any,1):.1f}%)")
    W(f"- minimal cost > planted: {gt} (must be 0: a minimal script can never exceed the "
      f"planted one)")
    tot_p = sum(r[0] for r in rows)
    tot_c = sum(r[2] for r in rows)
    W(f"- total planted symbol edits {tot_p}, total minimal cost {tot_c}: the census recovers "
      f"{100*tot_c/max(tot_p,1):.1f}% of planted symbol edits")
    W(f"- undercount per control: median {quant(under,.5):g}, p95 {quant(under,.95):g}, "
      f"max {max(under)}")
    W("\nUndercount happens when an edit is absorbed by a cheaper equivalent (an insertion "
      "next to a deletion becomes a substitution, a random inserted symbol equals its neighbour, "
      "an E3 duplicate equals the group it copies at an indel boundary). It is a property of "
      "minimal-edit reconstruction itself, measured here where the truth is known.\n")
    assert gt == 0, "minimal cost exceeded planted cost: the aligner is wrong"
    open(os.path.join(ROOT, "results", "adfgvx-census-validation.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
