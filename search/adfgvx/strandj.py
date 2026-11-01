"""Strand J, exactly as pre-registered in findings/adfgvx-1918-prereg.md (lead-adfgvx 8a1bcf8,
section 'Strand J' and its Revision 2). comp-adfgvx, 2026-11-01.

    nice -n 10 ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/strandj.py STEP

STEP, in the prereg's order (each is committed and pushed before the next runs):
  j0          pool, plant-side controls, groups (decryption-free)    -> results/adfgvx-J0.{md,json}
  j1-null     per-target / per-control nulls                           -> results/adfgvx-J1-nulls.jsonl
  j1-controls positive controls                                        -> results/adfgvx-J1-controls.jsonl
  j1-targets  targets                                                  -> results/adfgvx-J1-targets.jsonl
  j2-null     J2 test list + per-test nulls                            -> results/adfgvx-J2-nulls.jsonl
  j2-run      J2 tests                                                 -> results/adfgvx-J2-runs.jsonl
  j3-null     J3 group list + per-group nulls                          -> results/adfgvx-J3-nulls.jsonl
  j3-run      J3 groups                                                -> results/adfgvx-J3-runs.jsonl
  creilly     robustness re-run of J1-J3 statistics on creilly text    -> results/adfgvx-J-creilly.jsonl
  report      results/adfgvx-J.md from the records
Every run is appended to results/adfgvx-trials.log.

Implementation choices the prereg leaves open (fixed here, before J1 meets unread text):
  - 'parenthesised symbol': every symbol printed inside parentheses, a single one as in F(X)DFA or
    a whole group as in (DDAGD); parentheses containing lower case or spaces are annotation notes
    and contribute no symbols. Taken from the blind pass's printed block lines; checked against
    the final transcription's `symbols`.
  - 'flagged' (duplicate screen): FLAG against a SOLVED entry (p_entry < 0.01). Entries flagged
    only against another unread entry stay in the pool (they have no known key to control on).
  - 'cut to t's length': a uniformly random window of an eligible entry at least that long; if no
    single eligible entry is long enough, eligible entries are concatenated in random order and
    the window is cut from that.
  - Candidate keys: periods.assign over the solved entries' derived ranges (leave-in, as in
    results/adfgvx-clusters-scan.md), restricted to the 14 Lasry keys; p201D adds
    chi_2017_comments. An entry with no candidate gets no J1 test and is reported.
  - J2/J3 blank square cells: filled once per key with its unused symbols in an order fixed by
    a seed derived from the key id; the same fill in the run and in its null.
"""
import datetime
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
import lm  # noqa: E402
import periods  # noqa: E402
import power  # noqa: E402
import sharing  # noqa: E402
from headers import parse, page_date  # noqa: E402
from provenance import header as prov_header  # noqa: E402

PREREG = ("findings/adfgvx-1918-prereg.md @ lead-adfgvx 8a1bcf8 (Strand J + Revision 2: G1 60x "
          "nulls; G2 per-(group, square) J2 null and key-based J1(b) exclusion), clarifications "
          "C1-C2 and amendment C3 @ cd85680/91996a0, referee Part H conditions H1-H3 @ 91996a0")
HEADER_TOL = 10   # H3
LET = set("ADFGVX")
LASRY = periods.LASRY
RES = os.path.join(ROOT, "results")
CT = os.path.join(ROOT, "ciphertexts")
SEED = {"j1": 71001, "j2": 72001, "j3": 73001, "fill": 74001}
NULL_MULT = 60
MIN_LETTERS = 60
J2_MIN, J3_MIN = 300, 700
CAP = 2


# ------------------------------------------------------------------ helpers
def letters(s):
    return sum(c in LET for c in s)


def log_trial(step, **kw):
    kw = dict(step=step, utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **kw)
    with open(os.path.join(RES, "adfgvx-trials.log"), "a") as f:
        f.write(json.dumps(kw, sort_keys=True) + "\n")


def keys():
    return {k["id"]: k for k in json.load(open(os.path.join(CT, "adfgvx-1918-log.keys.json")))}


def records():
    return json.load(open(os.path.join(CT, "adfgvx-1918-log.records.json")))


def note_slots(note):
    """C1: a note that states a count of missing symbols or groups inserts that many lost slots
    (5 per group); any other note inserts nothing. Words are never read as symbols."""
    import re
    m = re.search(r"(\d+)\s*(group|letter|symbol|character)", note.lower())
    if not m:
        return 0
    n = int(m.group(1))
    return 5 * n if m.group(2) == "group" else n


def policy_from_lines(lines):
    """Printed block lines -> (stripped symbols, J0-policy pieces aligned to them).
    J0 policy with clarifications C1-C2 (prereg cd85680): a non-ADFGVX letter, a symbol inside
    parentheses (a whole parenthesised group: five), '-' and '?' are each one lost slot.
    Parentheses whose content has lower case or spaces are notes: no symbols, but a stated
    missing count inserts that many lost slots at the note's position (prefixed to the next
    printed symbol; suffixed to the last if the note ends the block)."""
    text = " ".join(lines)
    raw, pol = [], []
    pend = ""
    i = 0
    while i < len(text):
        c = text[i]
        if c == "(":
            j = text.index(")", i)
            inner = text[i + 1:j]
            if any(ch.islower() for ch in inner) or " " in inner or not inner:
                pend += "-" * note_slots(inner)
                i = j + 1
                continue
            for ch in inner:
                if ch.isspace():
                    continue
                raw.append(ch)
                pol.append(pend + "-")
                pend = ""
            i = j + 1
            continue
        if c.isspace():
            i += 1
            continue
        raw.append(c)
        pol.append(pend + (c if c in LET else "-"))
        pend = ""
        i += 1
    if pend:
        pol[-1] += pend
    return "".join(raw), pol


def blind_blocks():
    b = json.load(open(os.path.join(CT, "adfgvx-1918-scan-blind.json")))
    out = {}
    for pg in b["pages"]:
        for blk in pg["blocks"]:
            out[(pg["pdf_page"], blk["block_index"])] = blk
    return out


def j0_units():
    """Units of the primary transcription with the J0 symbol policy. Entry structure as
    search/adfgvx/scan.py (the prereg's joins and splits; p220C excluded)."""
    import scan
    d = json.load(open(scan.SCAN))
    E = {k: v for k, v in d["entries"].items() if v["set"] == "unsolved"}
    BB = blind_blocks()
    us, changes = scan.units()
    out = []
    for u in us:
        pieces_raw, pieces_pol = [], []
        for cid in u["ids"]:
            v = E[cid]
            for si, (pg, blk, a, b) in enumerate(v["spans"]):
                if len(v["spans"]) > 1 and u["unit"] != f"{cid}#{si+1}":
                    continue
                raw, pol = policy_from_lines(BB[(pg, blk)]["lines"])
                pieces_raw.append(raw[a:b])
                pieces_pol.append("".join(pol[a:b]))
        raw = "".join(pieces_raw)
        pol = "".join(pieces_pol)
        # H1: C1 note positions come from the transcription's `lines` field. Check that the
        # entry's `lines` give exactly the same policy text as the blind block lines used here.
        if len(u["ids"]) == 1:
            v = E[u["ids"][0]]
            lraw, lpol = policy_from_lines(v["lines"])
            assert lraw == v["symbols"], ("lines field does not reproduce symbols", u["unit"])
            whole = "".join(lpol)
            if len(v["spans"]) == 1:
                assert whole == pol, ("lines-field policy differs", u["unit"])
            else:
                si = int(u["unit"].split("#")[1]) - 1
                a = sum(b_ - a_ for (_, _, a_, b_) in v["spans"][:si])
                b = a + v["spans"][si][3] - v["spans"][si][2]
                assert "".join(lpol[a:b]) == pol, ("lines-field policy differs", u["unit"])
        assert raw == u["printed_scan"], ("blind lines do not reproduce the transcription", u["unit"])
        net = u["net"] or "RICHI"     # p148A, p215A.3: none printed -> treated like RICHI
        if u["unit"] == "p071A2":     # C3: part 2 of p071A1's message, which is CHI
            net = "CHI"
        out.append(dict(u, j0=pol, net_j0=net))
    return out, changes


# ------------------------------------------------------------------ J0
def candidates_for(sched_per, sol, unit):
    d, m = unit["page_date"]
    pdate = datetime.date(1918, m, d)
    h = parse(unit["heading"], pdate)
    if unit["heading_date"]:
        hd, hm = unit["heading_date"]
        h["dates"] = {datetime.date(1918, hm, hd)}
    c, basis = periods.assign(sched_per, pdate, h["dates"])
    c = {k for k in c if k in LASRY}
    label = periods.label(sched_per, c, pdate)
    return c, basis, label, pdate, h["dates"]


def run_j0():
    us, changes = j0_units()
    rec = records()
    by = {e["id"]: e for e in rec}
    sol = [e for e in rec if e["status"].startswith("Solved") and e["key"] in LASRY]
    for e in sol:
        e["_pd"] = page_date(e["date"])
        e["_h"] = parse(e["header"], e["_pd"])
    per = periods.derive(sol)
    # duplicate screen on the J0 texts
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "adfgvx-j0-units.json")
    json.dump([{"id": u["unit"], "printed": u["j0"]} for u in us], open(tmp, "w"))
    subprocess.check_call([sys.executable, "-I", os.path.join(HERE, "duplicates.py"), "--units", tmp,
                           "--tag", "J0"])
    import csv
    dup = {r["unread"]: r for r in csv.DictReader(l for l in open(os.path.join(RES, "adfgvx-duplicates-J0.csv"))
                                                  if not l.startswith("#"))}
    es, side = lm.split()
    rows = []
    for u in us:
        c, basis, label, pdate, hd = candidates_for(per, sol, u)
        if u["unit"] == "p201D":
            c = c | {"chi_2017_comments"}
        r = dup.get(u["unit"], {})
        flagged = bool(r.get("p_entry_solved")) and float(r["p_entry_solved"]) < 0.01
        twin = r.get("best_solved") if flagged else None
        rows.append(dict(
            unit=u["unit"], ids=u["ids"], childs_page=u["childs_page"], heading=u["heading"],
            page_date=str(pdate), heading_dates=sorted(map(str, hd)), net=u["net_j0"],
            n_slots=len(u["j0"]), n_letters=letters(u["j0"]), n_lost=u["j0"].count("-"),
            candidates=sorted(c, key=lambda k: (LASRY + ["chi_2017_comments"]).index(k)),
            derived_period=label, basis=basis,
            flagged=flagged, twin=twin, twin_key=by[twin]["key"] if twin else None,
            twin_side=side[twin][0] if twin and twin in side else None,
            twin_d=float(r["d_solved"]) if flagged else None,
            twin_cost=round(float(r["d_solved"]) * len(u["j0"])) if flagged else None,
            header_count=u["header_count"],
            header_short=(u["header_count"] - len(u["j0"])) if u["header_count"] is not None
            and abs(u["header_count"] - len(u["j0"])) > HEADER_TOL else None,
            text=u["j0"]))
    pool = [r for r in rows if not r["flagged"] and r["n_letters"] >= MIN_LETTERS]
    short = [r for r in rows if not r["flagged"] and r["n_letters"] < MIN_LETTERS]
    controls = [r for r in rows if r["flagged"]]
    groups = defaultdict(list)
    for r in pool:
        if r["net"] == "CHI":
            continue
        if r["derived_period"] in LASRY:
            groups[r["derived_period"]].append(r["unit"])
    amb = [r for r in pool if r["net"] != "CHI" and r["derived_period"] not in LASRY]
    J0 = dict(prereg=PREREG, changes=changes, rows=rows,
              pool=[r["unit"] for r in pool], too_short=[r["unit"] for r in short],
              controls_plant=[r["unit"] for r in controls if r["twin_side"] == "plant"],
              controls_train=[r["unit"] for r in controls if r["twin_side"] != "plant"],
              groups={g: m for g, m in sorted(groups.items())},
              ambiguous_pool=[r["unit"] for r in amb],
              header_mismatch={r["unit"]: r["header_short"] for r in rows if r["header_short"] is not None},
              no_header_count=[r["unit"] for r in rows if r["header_count"] is None],
              T=len(pool))
    json.dump(J0, open(os.path.join(RES, "adfgvx-J0.json"), "w"), indent=1)
    write_j0_md(J0)
    log_trial("J0", pool=len(pool), controls=len(controls), groups=len(groups))
    print(f"J0: {len(rows)} units, pool T={len(pool)}, controls {len(controls)} "
          f"(plant {len(J0['controls_plant'])}), too short {len(short)}, groups {len(groups)}")


def write_j0_md(J0):
    L = []
    W = L.append
    W("# Strand J, J0: pool, positive controls and groups (frozen before J1)\n")
    W(prov_header("", "search/adfgvx/strandj.py j0",
                  "transcription: PRIMARY = ciphertexts/adfgvx-1918-scan-transcription.json "
                  "(field symbols; parentheses and notes from the blind pass's block lines), J0 "
                  "symbol policy; solved side of the duplicate screen = creilly @ e60da03"))
    W(f"Binding text: {PREREG}. Decryption-free: headers, letter counts and the duplicate screen "
      f"(results/adfgvx-duplicates-J0.md) only.\n")
    W(f"- Entry structure: {J0['changes']}.")
    W("- Symbol policy: a non-ADFGVX letter, every symbol printed inside parentheses, `-` and `?` "
      "are each one lost symbol; notes in parentheses give no symbols; no alternatives tried.")
    W("- Notes (C1, prereg cd85680): not ciphertext; a stated missing count inserts that many lost "
      "slots at the note's position (5 per group), otherwise nothing. Here only p0924#2's "
      "'(missed 20 groups)' states one: 100 lost slots.")
    W("- C1 note positions are taken from the transcription's `lines` field (H1), asserted equal "
      "to the blind block lines for every unit: p0924#1 = 290 slots, nothing inserted; p0924#2 = "
      "358 slots, slots 200-299 lost.")
    W("- Net: the scan's `net`; none printed (p148A, p215A.3) is treated like RICHI.")
    W("- **AMENDMENT C3** (referee H2; heading evidence only, before any decryption): p071A2, whose "
      "scan `net` reads RICHI, is treated as CHI (part 2 of p071A1's message). It is ungrouped, and "
      "keeps its derived-period J1 candidates. **oct04 is reported without p071A2.** Not tested: "
      "p071A2 as RICHI, both parts as RICHI.")
    W("- Flagged = FLAG against a solved entry in the duplicate screen (p_entry < 0.01, its "
      "committed threshold). Flagged entries leave the pool and are the positive controls.")
    W(f"\n**Pool: T = {J0['T']}** unflagged entries with >= {MIN_LETTERS} ADFGVX letters. Too short: "
      f"{', '.join(J0['too_short']) or 'none'}. Plant-side controls: {len(J0['controls_plant'])}; "
      f"train-side (leakage-inflated): {len(J0['controls_train'])}.\n")
    W("| unit | page | heading date | net | slots | header count | letters | lost | candidates (J1) | derived period | role | twin (key, side, d, cost) |")
    W("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in J0["rows"]:
        role = ("control (plant)" if r["twin_side"] == "plant" else "control (train)") if r["flagged"] else \
               ("POOL" if r["unit"] in J0["pool"] else "too short")
        tw = f"{r['twin']} ({r['twin_key']}, {r['twin_side']}, {r['twin_d']:.3f}, {r['twin_cost']})" if r["flagged"] else ""
        W(f"| {r['unit']} | {r['childs_page']} | {','.join(r['heading_dates'])} | {r['net']} | "
          f"{r['n_slots']} | {r['header_count'] if r['header_count'] is not None else '-'} | {r['n_letters']} | {r['n_lost']} | {' '.join(r['candidates']) or '(none)'} | "
          f"{r['derived_period']} | {role} | {tw} |")
    W("\n## Groups for J2/J3: pool entries by single derived period, regardless of net; CHI not grouped\n")
    W("| group | members | letters | J2 (>= 300) | J3 (>= 700) |")
    W("|---|---|---|---|---|")
    let = {r["unit"]: r["n_letters"] for r in J0["rows"]}
    for g, m in J0["groups"].items():
        t = sum(let[u] for u in m)
        W(f"| {g} | {' '.join(m)} | {t} | {'yes' if t >= J2_MIN else 'no'} | {'yes' if t >= J3_MIN else 'no'} |")
    W(f"\nAmbiguous-period pool entries (not grouped; only the nov07/nov10 group enters J2, under "
      f"both squares): " + ", ".join(f"{u} ({next(r['derived_period'] for r in J0['rows'] if r['unit']==u)})"
                                     for u in J0["ambiguous_pool"]) + ".\n")
    W(f"## Units whose slot count differs from the header count by more than {HEADER_TOL} (H3)\n")
    W("A J1 negative for one of these reads \"uninformative: N symbols short of the header\", not "
      "the ~91% coverage sentence.\n")
    W("| unit | slots | header count | short by | role |")
    W("|---|---|---|---|---|")
    for u, n in J0["header_mismatch"].items():
        r = next(r for r in J0["rows"] if r["unit"] == u)
        role = "pool" if u in J0["pool"] else ("control" if r["flagged"] else "too short")
        W(f"| {u} | {r['n_slots']} | {r['header_count']} | {n} | {role} |")
    W(f"\nNo header count printed (H3 cannot be applied): {', '.join(J0['no_header_count'])}.\n")
    open(os.path.join(RES, "adfgvx-J0.md"), "w").write("\n".join(L) + "\n")

# ------------------------------------------------------------------ J1
# Scorer, cap and blank-cell charge exactly as power.py F3 (ef93381): jattack MODE 3, CAP 2,
# penalised trigram mean (PEN = ln(1/36) per trigram containing an unknown), LM on lm.split's
# TRAIN side. Since ef93381 jattack.c has only gained diagnostic output (bestev/bestsym), not a
# change to the score or the search.
N_HALF = None          # set from J0: 60*T/2 draws per half
BATCH = 64             # jattack MAXM
J1_NULL = {h: os.path.join(RES, f"adfgvx-J1-nulls-{h}.jsonl") for h in "ab"}
PEN = -3.58351893845611


def j0():
    return json.load(open(os.path.join(RES, "adfgvx-J0.json")))


def j1_subjects(J):
    """Targets (the pool), plant-side controls, train-side controls: unit, role, text, keys."""
    R = {r["unit"]: r for r in J["rows"]}
    out = []
    for role, units in (("target", J["pool"]), ("control-plant", J["controls_plant"]),
                        ("control-train", J["controls_train"])):
        for u in units:
            r = R[u]
            if r["candidates"]:
                out.append(dict(unit=u, role=role, text=r["text"], keys=r["candidates"],
                                twin_key=r["twin_key"]))
    return out


def dseed(*parts):
    return int(hashlib.sha256(":".join(map(str, (SEED["j1"],) + parts)).encode()).hexdigest()[:16], 16)


def plant_bank():
    """Null half (b): plant-side solved entries (lm.split) with a known key and printed text, as
    printed (creilly @ e60da03; '-' kept), sorted by id."""
    es, side = lm.split()
    out = []
    for e in records():
        if e["id"] in side and side[e["id"]][0] == "plant" and e["key"] and e["printed"]:
            out.append(dict(id=e["id"], key=e["key"],
                            text="".join(c if c in LET else "-" for c in e["printed"])))
    return sorted(out, key=lambda e: e["id"])


def draw_a(sub, i):
    rng = random.Random(dseed(sub["unit"], "a", i))
    t = list(sub["text"])
    rng.shuffle(t)
    return "".join(t), "shuffle"


def draw_b(sub, i, bank):
    """A plant-side solved entry whose key is not among the subject's candidates, cut to its
    length: entry uniform among eligible entries at least that long, then a uniform window; if
    none is long enough, all eligible entries concatenated in random order, uniform window."""
    rng = random.Random(dseed(sub["unit"], "b", i))
    L = len(sub["text"])
    elig = [e for e in bank if e["key"] not in sub["keys"]]
    long_ = [e for e in elig if len(e["text"]) >= L]
    if long_:
        e = rng.choice(long_)
        o = rng.randrange(len(e["text"]) - L + 1)
        return e["text"][o:o + L], f"{e['id']}@{o}"
    order = rng.sample(elig, len(elig))
    cat = "".join(e["text"] for e in order)
    o = rng.randrange(len(cat) - L + 1)
    return cat[o:o + L], "cat:" + "|".join(e["id"] for e in order[:4]) + f"...@{o}"


def mode3_job(key, texts):
    return (f"MODE 3\nSQUARE {key['square']}\nTRANS {len(key['transposition'])} "
            f"{' '.join(map(str, key['transposition']))}\nCAP {CAP}\n"
            + "".join(f"MSG {t}\n" for t in texts))


def run_mode3(key, texts):
    d = power.jattack(mode3_job(key, texts))
    out = []
    for m in range(len(texts)):
        out.append(dict(score=float(d[f"msg{m}_score"]), score0=float(d[f"msg{m}_score0"]),
                        edits=d[f"msg{m}_edits"].strip(), plain=d[f"msg{m}_plain"],
                        bestev=[float(x) for x in d[f"msg{m}_bestev"].split(",")]))
    return out


def py_pscore(text, edits, key, tab):
    """Independent-of-C replay: apply the edits (power.apply_edits_py), decrypt (engine), and
    take the penalised trigram mean. Must equal jattack's score."""
    from engine import decrypt
    v = power.apply_edits_py(text, edits.split(",") if edits else [])
    pl = decrypt(v, key["square"], key["transposition"])
    if len(pl) < 3:
        return -99.0, pl
    s = 0.0
    for i in range(2, len(pl)):
        a, b, c = pl[i - 2], pl[i - 1], pl[i]
        s += tab[lm.IDX[a] * 1296 + lm.IDX[b] * 36 + lm.IDX[c]] if (a in lm.IDX and b in lm.IDX and c in lm.IDX) else PEN
    return s / (len(pl) - 2), pl


def scorer_setup():
    """Compile jattack and write the LM table (train side) once; return (tab, sha of table)."""
    es, side, tab, N, plant, freq = power.build_tools(write=True)
    sha = hashlib.sha256(open(power.LMT, "rb").read()).hexdigest()
    return tab, sha


def run_j1_null(half):
    """Null records for one half, for every subject (targets and controls). Half 'b' reads no
    unread symbol (only each subject's length and candidate keys); half 'a' shuffles the
    subject's own text."""
    from concurrent.futures import ThreadPoolExecutor
    sharing.exclusive()
    J = j0()
    n_half = NULL_MULT * J["T"] // 2
    subs = j1_subjects(J)
    K = keys()
    bank = plant_bank()
    tab, lmsha = scorer_setup()
    jobs = []
    for sub in subs:
        draws = [draw_a(sub, i) if half == "a" else draw_b(sub, i, bank) for i in range(n_half)]
        for k in sub["keys"]:
            for i0 in range(0, n_half, BATCH):
                jobs.append((sub, k, i0, draws[i0:i0 + BATCH]))
    t0 = time.time()

    def work(job):
        sub, k, i0, dr = job
        res = run_mode3(K[k], [t for t, _ in dr])
        # replay the first draw of every job in Python (certificate of the score, not of the max)
        ps, _ = py_pscore(dr[0][0], res[0]["edits"], K[k], tab)
        assert abs(ps - res[0]["score"]) < 1e-4, ("replay mismatch", sub["unit"], k, i0, ps, res[0]["score"])
        return dict(unit=sub["unit"], role=sub["role"], half=half, key=k, i0=i0, n=len(dr),
                    src=[s for _, s in dr],
                    sha=[hashlib.sha256(t.encode()).hexdigest()[:12] for t, _ in dr],
                    score=[r["score"] for r in res], score0=[r["score0"] for r in res],
                    edits=[r["edits"] for r in res], bestev=[r["bestev"] for r in res])
    out = J1_NULL[half]
    with ThreadPoolExecutor(sharing.jobs(6)) as ex, open(out + ".part", "w") as f:
        f.write(json.dumps(dict(meta=True, prereg=PREREG, half=half, n_half=n_half, T=J["T"],
                                seed=SEED["j1"], cap=CAP, lm_sha256=lmsha,
                                jattack_sha256=hashlib.sha256(open(os.path.join(HERE, "jattack.c"), "rb").read()).hexdigest(),
                                provenance=prov_header("", f"search/adfgvx/strandj.py j1-null-{half}",
                                                       "transcription: PRIMARY (J0 texts); half b: creilly "
                                                       "@ e60da03 printed, plant-side solved entries"))) + "\n")
        done = 0
        for rec in ex.map(work, jobs):
            f.write(json.dumps(rec) + "\n")
            done += 1
            if done % 200 == 0:
                print(f"  {done}/{len(jobs)} jobs, {time.time() - t0:.0f}s", flush=True)
    os.replace(out + ".part", out)
    for sub in subs:
        log_trial(f"J1-null-{half}", unit=sub["unit"], role=sub["role"], keys=sub["keys"],
                  draws=n_half, runs=n_half * len(sub["keys"]), cap=CAP)
    print(f"J1 null half {half}: {len(subs)} subjects x {n_half} draws, {len(jobs)} jobs, "
          f"{time.time() - t0:.0f}s -> {out}")


def open_rec(path):
    """Records are committed gzipped when large (path + '.gz')."""
    import gzip
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt")
    return open(path)


def load_nulls():
    """Per subject: list of draw statistics max over keys (both halves), and per-key scores."""
    per = defaultdict(lambda: defaultdict(dict))   # unit -> (half, i) -> key -> score
    meta = {}
    for h in "ab":
        for l in open_rec(J1_NULL[h]):
            r = json.loads(l)
            if r.get("meta"):
                meta[h] = r
                continue
            for j, sc in enumerate(r["score"]):
                per[r["unit"]][(h, r["i0"] + j)][r["key"]] = sc
    return per, meta


def thresholds(subs, per, n_half):
    thr = {}
    for sub in subs:
        D = per[sub["unit"]]
        need = {(h, i) for h in "ab" for i in range(n_half)}
        assert set(D) == need, ("incomplete null", sub["unit"], len(D))
        stats = [max(D[x][k] for k in sub["keys"]) for x in sorted(need)]
        assert all(len(D[x]) == len(sub["keys"]) for x in need)
        thr[sub["unit"]] = dict(threshold=max(stats), n=len(stats),
                                p99=sorted(stats)[int(0.99 * len(stats))],
                                max_a=max(s for x, s in zip(sorted(need), stats) if x[0] == "a"),
                                max_b=max(s for x, s in zip(sorted(need), stats) if x[0] == "b"))
    return thr


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return (c - h, c + h)


def score_subjects(roles, outname, step):
    J = j0()
    n_half = NULL_MULT * J["T"] // 2
    subs = [s for s in j1_subjects(J) if s["role"] in roles]
    per, meta = load_nulls()
    tab, lmsha = scorer_setup()
    for h in "ab":
        assert meta[h]["lm_sha256"] == lmsha, "scorer changed since the null was recorded"
        assert meta[h]["n_half"] == n_half and meta[h]["cap"] == CAP
    thr = thresholds(subs, per, n_half)
    K = keys()
    out = []
    for sub in subs:
        byk = {}
        for k in sub["keys"]:
            r = run_mode3(K[k], [sub["text"]])[0]
            ps, pl = py_pscore(sub["text"], r["edits"], K[k], tab)
            assert abs(ps - r["score"]) < 1e-4, ("replay mismatch", sub["unit"], k)
            byk[k] = r
        best = max(sub["keys"], key=lambda k: byk[k]["score"])
        S = byk[best]["score"]
        t = thr[sub["unit"]]
        rec = dict(unit=sub["unit"], role=sub["role"], keys=sub["keys"], S=S, argmax=best,
                   threshold=t["threshold"], null_n=t["n"], null_p99=t["p99"],
                   null_max_a=t["max_a"], null_max_b=t["max_b"], above=S > t["threshold"],
                   edits=byk[best]["edits"], bestev=byk[best]["bestev"],
                   jump=[byk[best]["bestev"][i] - byk[best]["bestev"][i - 1]
                         for i in range(1, len(byk[best]["bestev"]))],
                   per_key={k: dict(score=byk[k]["score"], score0=byk[k]["score0"],
                                    edits=byk[k]["edits"], bestev=byk[k]["bestev"]) for k in sub["keys"]},
                   plain=byk[best]["plain"], twin_key=sub["twin_key"])
        if sub["role"].startswith("control"):
            rec["detected"] = rec["above"] and best == sub["twin_key"]
        out.append(rec)
        log_trial(step, unit=sub["unit"], role=sub["role"], keys=sub["keys"], cap=CAP,
                  runs=len(sub["keys"]), S=S, threshold=t["threshold"], above=rec["above"])
    with open(os.path.join(RES, outname), "w") as f:
        f.write(json.dumps(dict(meta=True, prereg=PREREG, lm_sha256=lmsha, provenance=prov_header(
            "", f"search/adfgvx/strandj.py {step.lower()}", "transcription: PRIMARY (J0 texts)"))) + "\n")
        for r in out:
            f.write(json.dumps(r) + "\n")
    return out


def run_j1_controls():
    out = score_subjects(("control-plant", "control-train"), "adfgvx-J1-controls.jsonl", "J1-controls")
    for role in ("control-plant", "control-train"):
        R = [r for r in out if r["role"] == role]
        k = sum(r["detected"] for r in R)
        lo, hi = wilson(k, len(R))
        print(f"{role}: detected {k}/{len(R)} (Wilson {100*lo:.0f}-{100*hi:.0f}%)")
        for r in R:
            print(f"  {r['unit']:14s} S {r['S']:.4f} thr {r['threshold']:.4f} argmax {r['argmax']} "
                  f"twin {r['twin_key']} {'DETECTED' if r['detected'] else ''}")


def run_j1_targets():
    out = score_subjects(("target",), "adfgvx-J1-targets.jsonl", "J1-targets")
    for r in out:
        print(f"  {r['unit']:14s} S {r['S']:.4f} thr {r['threshold']:.4f} argmax {r['argmax']} "
              f"{'DETECTION' if r['above'] else ''}")
    print(f"J1 targets: {sum(r['above'] for r in out)}/{len(out)} above threshold")


# ------------------------------------------------------------------ J2 / J3
# J2: the group's period square (blank cells filled once per key, seed SEED['fill'] + key id, the
# same fill in the run and its null), jattack MODE 2, widths 15-22, power.py F2 budget (ef93381).
# J3: jattack MODE 1, widths 15-22, power.py F1 budget. Statistic: best_pscore (penalised).
# Null halves: (a) the test's members, each shuffled; (b) plant-side solved text cut to each
# member's length (J1's cut rule): J2 - each member independently from an entry whose key's
# square differs from the test's square; J3 - members from pairwise different keys.
J2_NULL = os.path.join(RES, "adfgvx-J2-nulls.jsonl")
J3_NULL = os.path.join(RES, "adfgvx-J3-nulls.jsonl")
AMB = "ambiguous between nov07 and nov10"


def gseed(*parts):
    return dseed(*parts) % (2 ** 31 - 1)


def filled_square(kid):
    rng = random.Random(dseed("fill", SEED["fill"], kid))
    sq = list(keys()[kid]["square"])
    free = [c for c in lm.ALPH if c not in sq]
    rng.shuffle(free)
    return "".join(free.pop() if c == "?" else c for c in sq)


def j1_detected():
    out = set()
    for l in open(os.path.join(RES, "adfgvx-J1-targets.jsonl")):
        r = json.loads(l)
        if not r.get("meta") and r["above"]:
            out.add(r["unit"])
    return out


def j2_detected():
    p = os.path.join(RES, "adfgvx-J2-runs.jsonl")
    out = set()
    for l in open(p):
        r = json.loads(l)
        if not r.get("meta") and r["above"]:
            out.add(r["test"])
    return out


def j2_tests():
    J = j0()
    R = {r["unit"]: r for r in J["rows"]}
    det = j1_detected()
    tests, excluded = [], []
    for g, mem in J["groups"].items():
        m = [u for u in mem if u not in det]
        let = sum(R[u]["n_letters"] for u in m)
        if let >= J2_MIN:
            tests.append(dict(test=g, group=g, square_key=g, members=m, letters=let, extra=False))
    amb = [u for u in J["ambiguous_pool"] if R[u]["derived_period"] == AMB and u not in det]
    for sk in ("nov07", "nov10"):
        tests.append(dict(test=f"nov07/nov10@{sk}", group="nov07/nov10", square_key=sk, members=amb,
                          letters=sum(R[u]["n_letters"] for u in amb), extra=True))
    other = [u for u in J["ambiguous_pool"] if R[u]["derived_period"] != AMB and u not in det]
    G = sum(not t["extra"] for t in tests)
    return tests, dict(G=G, G_prime=G + 2, n=NULL_MULT * (G + 2), j1_detections=sorted(det),
                       excluded_ambiguous=other,
                       excluded_letters=sum(R[u]["n_letters"] for u in other))


def j3_tests():
    J = j0()
    R = {r["unit"]: r for r in J["rows"]}
    det = j1_detected()
    det2 = {t.split("@")[0] for t in j2_detected()}
    tests = []
    for g, mem in J["groups"].items():
        if g in det2:
            continue
        m = [u for u in mem if u not in det]
        let = sum(R[u]["n_letters"] for u in m)
        if let >= J3_MIN:
            tests.append(dict(test=g, group=g, members=m, letters=let))
    return tests, dict(G3=len(tests), n=NULL_MULT * len(tests), j1_detections=sorted(det),
                       j2_detections=sorted(det2))


def cut(rng, elig, L):
    long_ = [e for e in elig if len(e["text"]) >= L]
    if long_:
        e = rng.choice(long_)
        o = rng.randrange(len(e["text"]) - L + 1)
        return e["text"][o:o + L], f"{e['id']}@{o}", e["key"]
    order = rng.sample(elig, len(elig))
    cat = "".join(e["text"] for e in order)
    o = rng.randrange(len(cat) - L + 1)
    return cat[o:o + L], "cat:" + "|".join(e["id"] for e in order[:4]) + f"...@{o}", order[0]["key"]


def group_draw(fam, test, texts, half, i, bank, K):
    rng = random.Random(dseed(fam, test["test"], half, i))
    if half == "a":
        out = []
        for t in texts:
            x = list(t)
            rng.shuffle(x)
            out.append("".join(x))
        return out, ["shuffle"] * len(texts), [None] * len(texts)
    msgs, src, ks = [], [], []
    if fam == "j2":
        sq = K[test["square_key"]]["square"]
        elig = [e for e in bank if e["key"] in K and K[e["key"]]["square"] != sq]
        for t in texts:
            m, sr, k = cut(rng, elig, len(t))
            msgs.append(m); src.append(sr); ks.append(k)
    else:   # j3: members from pairwise different keys, longest member first
        used = set()
        res = [None] * len(texts)
        for j in sorted(range(len(texts)), key=lambda j: -len(texts[j])):
            elig = [e for e in bank if e["key"] not in used]
            kk = sorted({e["key"] for e in elig if len(e["text"]) >= len(texts[j])}) or sorted({e["key"] for e in elig})
            k = rng.choice(kk)
            m, sr, _ = cut(rng, [e for e in elig if e["key"] == k], len(texts[j]))
            used.add(k)
            res[j] = (m, sr, k)
        msgs, src, ks = [list(x) for x in zip(*res)]
    return msgs, src, ks


def group_job(fam, msgs, seed, freq, square=None):
    return power.job_text(2 if fam == "j2" else 1, msgs, seed, freq, square)


def run_group_null(fam):
    from concurrent.futures import ThreadPoolExecutor
    sharing.exclusive()
    tests, info = j2_tests() if fam == "j2" else j3_tests()
    J = j0()
    R = {r["unit"]: r for r in J["rows"]}
    K = keys()
    bank = plant_bank()
    es, side, tab, N, plant, freq = power.build_tools(write=True)
    lmsha = hashlib.sha256(open(power.LMT, "rb").read()).hexdigest()
    n_half = info["n"] // 2
    jobs = []
    for t in tests:
        texts = [R[u]["text"] for u in t["members"]]
        sq = filled_square(t["square_key"]) if fam == "j2" else None
        for h in "ab":
            for i in range(n_half):
                jobs.append((t, h, i, texts, sq))
    t0 = time.time()

    def work(job):
        t, h, i, texts, sq = job
        msgs, src, ks = group_draw(fam, t, texts, h, i, bank, K)
        assert [len(m) for m in msgs] == [len(x) for x in texts]
        seed = gseed(fam, t["test"], h, i, "jat")
        d = power.jattack(group_job(fam, msgs, seed, freq, sq))
        return dict(test=t["test"], half=h, i=i, seed=seed, src=src, keys=ks,
                    pscore=float(d["best_pscore"]), score=float(d["best_score"]),
                    width=int(d["best_width"]), cpu=d["_cpu"])
    out = J2_NULL if fam == "j2" else J3_NULL
    with ThreadPoolExecutor(sharing.jobs(6)) as ex, open(out + ".part", "w") as f:
        f.write(json.dumps(dict(meta=True, prereg=PREREG, fam=fam, tests=tests, info=info, n_half=n_half,
                                widths=power.WIDTHS, budget=power.BUDGET["F2" if fam == "j2" else "F1"],
                                squares={t["test"]: filled_square(t["square_key"]) for t in tests} if fam == "j2" else None,
                                lm_sha256=lmsha, freq=freq,
                                provenance=prov_header("", f"search/adfgvx/strandj.py {fam}-null",
                                                       "transcription: PRIMARY (J0 texts); half b: creilly "
                                                       "@ e60da03 printed, plant-side solved entries"))) + "\n")
        done = 0
        for rec in ex.map(work, jobs):
            f.write(json.dumps(rec) + "\n")
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(jobs)} draws, {time.time() - t0:.0f}s", flush=True)
    os.replace(out + ".part", out)
    for t in tests:
        log_trial(f"{fam.upper()}-null", test=t["test"], members=t["members"], letters=t["letters"],
                  draws=2 * n_half, widths=power.WIDTHS,
                  square=t.get("square_key"), extra=t.get("extra", False))
    print(f"{fam} null: {len(tests)} tests x {2 * n_half} draws, {time.time() - t0:.0f}s -> {out}")


def run_group_tests(fam):
    nullp = J2_NULL if fam == "j2" else J3_NULL
    lines = [json.loads(l) for l in open_rec(nullp)]
    meta = lines[0]
    tests, info = j2_tests() if fam == "j2" else j3_tests()
    assert [t["test"] for t in tests] == [t["test"] for t in meta["tests"]], "test list changed since the null"
    J = j0()
    R = {r["unit"]: r for r in J["rows"]}
    es, side, tab, N, plant, freq = power.build_tools(write=True)
    lmsha = hashlib.sha256(open(power.LMT, "rb").read()).hexdigest()
    assert lmsha == meta["lm_sha256"] and freq == meta["freq"], "scorer changed since the null"
    nulls = defaultdict(list)
    for r in lines[1:]:
        nulls[r["test"]].append(r)
    out = []
    for t in tests:
        N_ = nulls[t["test"]]
        assert len(N_) == 2 * meta["n_half"], ("incomplete null", t["test"], len(N_))
        thr = max(r["pscore"] for r in N_)
        texts = [R[u]["text"] for u in t["members"]]
        sq = filled_square(t["square_key"]) if fam == "j2" else None
        if fam == "j2":
            assert sq == meta["squares"][t["test"]]
        seed = gseed(fam, t["test"], "run")
        d = power.jattack(group_job(fam, texts, seed, freq, sq))
        ps = float(d["best_pscore"])
        rec = dict(test=t["test"], members=t["members"], letters=t["letters"], seed=seed,
                   pscore=ps, score=float(d["best_score"]), threshold=thr, null_n=len(N_),
                   null_max_a=max(r["pscore"] for r in N_ if r["half"] == "a"),
                   null_max_b=max(r["pscore"] for r in N_ if r["half"] == "b"),
                   above=ps > thr, width=int(d["best_width"]), trans=d["best_trans"],
                   square=d["best_square"], square_key=t.get("square_key"), extra=t.get("extra", False),
                   plain={u: d[f"best_plain{m}"] for m, u in enumerate(t["members"])}, cpu=d["_cpu"])
        out.append(rec)
        log_trial(f"{fam.upper()}-run", test=t["test"], members=t["members"], widths=power.WIDTHS,
                  square=t.get("square_key"), pscore=ps, threshold=thr, above=rec["above"])
        print(f"  {t['test']:22s} pscore {ps:.4f} thr {thr:.4f} width {rec['width']} "
              f"{'DETECTION' + (' (LEAD)' if fam == 'j3' else '') if rec['above'] else ''}", flush=True)
    with open(os.path.join(RES, f"adfgvx-{fam.upper()}-runs.jsonl"), "w") as f:
        f.write(json.dumps(dict(meta=True, prereg=PREREG, lm_sha256=lmsha, provenance=prov_header(
            "", f"search/adfgvx/strandj.py {fam}-run", "transcription: PRIMARY (J0 texts)"))) + "\n")
        for r in out:
            f.write(json.dumps(r) + "\n")
    print(f"{fam}: {sum(r['above'] for r in out)}/{len(out)} above threshold")


# ------------------------------------------------------------------ creilly robustness re-run
# Prereg: detection is defined on the primary only; the creilly re-run cannot add a detection.
# Fixed here before it runs: each J0 unit's text is rebuilt from creilly `printed` @ e60da03
# (ids joined in J0 order; a split unit is cut at the scan's block boundary, p0924#1 = first 290
# symbols); every non-ADFGVX symbol is one lost slot. The SAME statistics (J1 S_t under the same
# candidates and cap; J2/J3 pscore with the same seeds, squares and budgets) are compared with
# the PRIMARY thresholds. Those thresholds were drawn at the primary texts' lengths, so where
# the lengths differ the comparison is approximate, and the report says so per entry.
def creilly_texts():
    J = j0()
    rec = {e["id"]: e for e in records()}
    out = {}
    for r in J["rows"]:
        ids = list(dict.fromkeys(r["ids"]))
        c = "".join(rec[i]["printed"] or "" for i in ids)
        c = "".join(ch if ch in LET else "-" for ch in c)
        if r["unit"] == "p0924#1":
            c = c[:290]
        elif r["unit"] == "p0924#2":
            c = c[290:]
        out[r["unit"]] = c
    return out


def run_creilly():
    J = j0()
    R = {r["unit"]: r for r in J["rows"]}
    CT_ = creilly_texts()
    K = keys()
    es, side, tab, N, plant, freq = power.build_tools(write=True)
    out = []
    for r in _jsonl("adfgvx-J1-targets.jsonl"):
        t = CT_[r["unit"]]
        byk = {k: run_mode3(K[k], [t])[0] for k in r["keys"]}
        best = max(r["keys"], key=lambda k: byk[k]["score"])
        rec = dict(stage="J1", unit=r["unit"], len_primary=R[r["unit"]]["n_slots"], len_creilly=len(t),
                   S=byk[best]["score"], argmax=best, edits=byk[best]["edits"],
                   threshold_primary=r["threshold"], above_primary_threshold=byk[best]["score"] > r["threshold"],
                   S_primary=r["S"], primary_detection=r["above"])
        out.append(rec)
        log_trial("creilly-J1", unit=r["unit"], keys=r["keys"], cap=CAP, runs=len(r["keys"]), S=rec["S"])
    for fam in ("j2", "j3"):
        rr = _jsonl(f"adfgvx-{fam.upper()}-runs.jsonl") or []
        for r in rr:
            texts = [CT_[u] for u in r["members"]]
            sq = filled_square(r["square_key"]) if fam == "j2" else None
            d = power.jattack(group_job(fam, texts, r["seed"], freq, sq))
            ps = float(d["best_pscore"])
            out.append(dict(stage=fam.upper(), test=r["test"], letters_creilly=sum(letters(x) for x in texts),
                            letters_primary=r["letters"], pscore=ps, threshold_primary=r["threshold"],
                            above_primary_threshold=ps > r["threshold"], pscore_primary=r["pscore"],
                            primary_detection=r["above"], width=int(d["best_width"])))
            log_trial(f"creilly-{fam.upper()}", test=r["test"], widths=power.WIDTHS, pscore=ps)
    with open(os.path.join(RES, "adfgvx-J-creilly.jsonl"), "w") as f:
        f.write(json.dumps(dict(meta=True, prereg=PREREG, provenance=prov_header(
            "", "search/adfgvx/strandj.py creilly", "transcription: SECONDARY = creilly11235/adfgvx-1918 "
            "@ e60da03 printed, rebuilt to the J0 units"))) + "\n")
        for r in out:
            f.write(json.dumps(r) + "\n")
    for r in out:
        print(r)


# ------------------------------------------------------------------ report
def _jsonl(name):
    p = os.path.join(RES, name)
    if not (os.path.exists(p) or os.path.exists(p + ".gz")):
        return None
    L = [json.loads(l) for l in open_rec(p)]
    return [r for r in L if not r.get("meta")]


def null_gain():
    """Per subject: the edit gain (score - score0, at the maximising key) of every null draw."""
    best = defaultdict(dict)    # unit -> (half,i) -> (score, gain)
    for h in "ab":
        p = J1_NULL[h]
        if not (os.path.exists(p) or os.path.exists(p + ".gz")):
            return None
        for l in open_rec(p):
            r = json.loads(l)
            if r.get("meta"):
                continue
            for j, (sc, s0) in enumerate(zip(r["score"], r["score0"])):
                x = (h, r["i0"] + j)
                if x not in best[r["unit"]] or sc > best[r["unit"]][x][0]:
                    best[r["unit"]][x] = (sc, sc - s0)
    return {u: sorted(g for _, g in D.values()) for u, D in best.items()}


def false_bound_text():
    """Revised false-detection bound (referee I1): the two null halves are not exchangeable;
    only half (a) (shuffled target text) supports a bound: k_family / (n_half + 1)."""
    J = j0()
    nb = [("J1", J["T"], NULL_MULT * J["T"] // 2)]
    for fam, path in (("J2", J2_NULL), ("J3", J3_NULL)):
        if os.path.exists(path) or os.path.exists(path + ".gz"):
            m = json.loads(next(iter(open_rec(path))))
            nb.append((fam, len(m["tests"]), m["n_half"]))
    parts = [f"{f} <= {k}/{n + 1} = {100 * k / (n + 1):.1f}%" for f, k, n in nb]
    return ("The prereg intended each family to be below 1/60, giving < 5% for the strand. That bound "
            "needs every null draw to be exchangeable with the target, and the two halves of the null "
            "are not: half (a), the target's own text shuffled, scores far above half (b), plant-side "
            "text with creilly's lower lost rate (null max (a) / (b) columns below). Only half (a) "
            f"supports a bound: **{', '.join(parts)}.** "
            "J1 <= 3.3% (half (a), and a mask-matched null, referee Part K); no bound for J2/J3 on "
            "damaged groups, so none for strand J as a whole. The thresholds themselves "
            "(the max over both halves) are unchanged, and so are the detections.\n")


def neg_label(J, u):
    n = J.get("header_mismatch", {}).get(u)
    if n is None:
        return "negative"
    return (f"negative; uninformative: {n} symbols short of the header" if n > 0 else
            f"negative; uninformative: {-n} symbols more than the header")


def run_report():
    J = j0()
    R = {r["unit"]: r for r in J["rows"]}
    L = []
    W = L.append
    W("# Strand J: results (comp-adfgvx)\n")
    W(prov_header("", "search/adfgvx/strandj.py report", "transcription: PRIMARY = ciphertexts/adfgvx-"
                  "1918-scan-transcription.json, J0 texts (results/adfgvx-J0.md)"))
    W(f"Binding text: {PREREG}. Each step's records were committed before the next step ran; "
      f"the order is in git. Every run is in results/adfgvx-trials.log.\n")
    W(f"J0: pool T = {J['T']}; plant-side controls {len(J['controls_plant'])}; train-side "
      f"controls {len(J['controls_train'])} (leakage-inflated); groups in results/adfgvx-J0.md.\n")
    recs = {e["id"]: e for e in records()}
    ctl = _jsonl("adfgvx-J1-controls.jsonl")
    tg = _jsonl("adfgvx-J1-targets.jsonl")
    gain = null_gain() if (ctl or tg) else None
    if ctl:
        W("## J1 positive controls\n")
        W("Detected = S above the control's own threshold (max of 60T draws) AND the maximising key "
          "is the twin's key. Twin cost = edit cost of the duplicate screen's fitting alignment.\n")
        for role, lab in (("control-plant", "Plant-side (the decision rule)"),
                          ("control-train", "Train-side (LEAKAGE-INFLATED: the twin's plaintext is in the scorer's training text)")):
            Rr = [r for r in ctl if r["role"] == role]
            k = sum(r["detected"] for r in Rr)
            lo, hi = wilson(k, len(Rr))
            W(f"**{lab}: {k}/{len(Rr)} detected ({100*k/len(Rr):.0f}%, Wilson 95% {100*lo:.0f}-{100*hi:.0f}%) [S, {datetime.date.today()}]**\n")
            W("| control | slots | twin (key) | twin length | twin d, cost | candidates | S | threshold | null max (a / b) | argmax | edits | detected |")
            W("|---|---|---|---|---|---|---|---|---|---|---|---|")
            for r in Rr:
                q = R[r["unit"]]
                W(f"| {r['unit']} | {q['n_slots']} | {q['twin']} ({q['twin_key']}) | {len(recs[q['twin']]['printed'])} | "
                  f"{q['twin_d']:.3f}, {q['twin_cost']} | "
                  f"{' '.join(r['keys'])} | {r['S']:.4f} | {r['threshold']:.4f} | {r['null_max_a']:.4f} / "
                  f"{r['null_max_b']:.4f} | {r['argmax']} | {r['edits'] or '-'} | "
                  f"{'yes' if r['detected'] else ('above, wrong key' if r['above'] else 'no')} |")
            W("")
        kp = sum(r["detected"] for r in ctl if r["role"] == "control-plant")
        np_ = sum(r["role"] == "control-plant" for r in ctl)
        W(("J1 is **UNDERPOWERED on real text** (fewer than 50% of plant-side controls detected); "
           "its negatives say so.\n") if kp < np_ / 2 else
          "Plant-side detection rate is at least 50%: J1 is not declared underpowered.\n")
        frag = [r for r in ctl if r["role"] == "control-plant"
                and len(recs[R[r["unit"]]["twin"]]["printed"]) > 1.1 * R[r["unit"]]["n_slots"]]
        full = [r for r in ctl if r["role"] == "control-plant" and r not in frag]
        W(f"Seen only after the result, descriptive, changing no rule [H]: {len(frag)} plant-side controls "
          f"are FRAGMENTS of their twin (twin more than 10% longer): {sum(r['detected'] for r in frag)}/"
          f"{len(frag)} detected. A partial copy of a columnar-transposed message is not a ciphertext of its "
          f"own length under the key, so a known-key decryption cannot read it. The other "
          f"{len(full)}: {sum(r['detected'] for r in full)}/{len(full)} detected. (p215A2, a fragment, could not "
          f"be detected in any case: its twin's key, nov25, is not among its candidates.)\n")
    if tg:
        W("## J1 targets\n")
        det = [r for r in tg if r["above"]]
        W(f"**Detections: {len(det)} of {len(tg)}** (S_t above threshold_t, the max of n_t = "
          f"{tg[0]['null_n']} draws). Thresholds and detections are as pre-registered and unchanged.\n")
        W("~~FWER <= sum 1/(n_t+1) < 1/60 (union bound, as stated in the prereg and accepted by the "
          "referee, Part G).~~ **SUPERSEDED (referee Part I, I1/I3; Part J, J1):**\n")
        W(false_bound_text())
        W(f"**J1 negatives: the measured detection rate on real text is {kp}/{np_} (Wilson "
          f"{100*wilson(kp, np_)[0]:.0f}-{100*wilson(kp, np_)[1]:.0f}%).** That is below the "
          f"pre-registered 50%, so J1 is formally UNDERPOWERED. The '~91%' figure is the cap's "
          f"coverage of the damage model, not power. So every J1 negative ({len(tg) - len(det)} entries) "
          f"reads as \"uninformative\" or \"not detected at low power\"; none is an exclusion. For the "
          f"H3 units the negative is uninformative, as marked.\n")
        W("~~A negative reads: no reading under the candidate period keys with <= 2 jattack edits "
          "(covering ~91% of messages under the damage model).~~ SUPERSEDED by the paragraph above "
          "(referee Part J, J1). The cap (<= 2 jattack edits, ~91% coverage under the damage model) "
          "describes the search, not its power.\n")
        W("A detection is a margin over the null, not a reading. Several detections show German at a "
          "glance; others (e.g. p170D, p218A, p220B) are mostly '-' or letter salad. READ-KNOWN-KEY "
          "needs check- reproduction and the adversary.\n")
        W("| target | letters | candidates | S | threshold | margin | argmax | edits | edit gain (S - S0) | null gain p99 / max | result |")
        W("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in tg:
            g = gain[r["unit"]] if gain else None
            gs = f"{g[int(0.99*len(g))]:.4f} / {g[-1]:.4f}" if g else ""
            W(f"| {r['unit']} | {R[r['unit']]['n_letters']} | {' '.join(r['keys'])} | {r['S']:.4f} | "
              f"{r['threshold']:.4f} | {r['S'] - r['threshold']:+.4f} | {r['argmax']} | {r['edits'] or '-'} | "
              f"{r['S'] - r['per_key'][r['argmax']]['score0']:.4f} | {gs} | "
              f"{'**DETECTION**' if r['above'] else neg_label(J, r['unit'])} |")
        W("")
        for r in det:
            W(f"- **{r['unit']}** under {r['argmax']}, edits `{r['edits']}`: S {r['S']:.4f} vs "
              f"threshold {r['threshold']:.4f}. Plaintext: `{r['plain']}`. This is a detection, not a "
              f"reading: READ-KNOWN-KEY needs check- and the adversary.")
        W("")
    for fam, title in (("J2", "J2: known square, unknown transposition (READ-JOINT, partial key)"),
                       ("J3", "J3: unknown square and transposition (detection only; a detection is a LEAD)")):
        rr = _jsonl(f"adfgvx-{fam}-runs.jsonl")
        if not rr:
            continue
        W(f"## {title}\n")
        W("| test | members | letters | pscore | threshold | null max (a / b) | width | result |")
        W("|---|---|---|---|---|---|---|---|")
        for r in rr:
            W(f"| {r['test']}{' (declared extra)' if r.get('extra') else ''} | {' '.join(r['members'])} | "
              f"{r['letters']} | {r['pscore']:.4f} | {r['threshold']:.4f} | {r['null_max_a']:.4f} / "
              f"{r['null_max_b']:.4f} | {r['width']} | "
              f"{('**DETECTION**' + (' (LEAD)' if fam == 'J3' else '')) if r['above'] else 'negative'} |")
        W("")
    cr = _jsonl("adfgvx-J-creilly.jsonl")
    if cr:
        W("## Robustness: the same statistics on creilly `printed` @ e60da03 (cannot add a detection)\n")
        W("Each J0 unit rebuilt from creilly's ids (p0924 cut at 290); the same candidates, cap, seeds, "
          "squares and budgets; compared with the PRIMARY thresholds, which were drawn at the primary "
          "lengths, so the comparison is approximate where the lengths differ.\n")
        c1 = [r for r in cr if r["stage"] == "J1"]
        pdet = [r for r in c1 if r["primary_detection"]]
        W(f"- J1: of {len(pdet)} primary detections, {sum(r['above_primary_threshold'] for r in pdet)} are "
          f"also above threshold on creilly's text.")
        W("\n| unit | slots primary / creilly | S primary | S creilly | threshold (primary) | creilly above? |")
        W("|---|---|---|---|---|---|")
        for r in c1:
            if r["primary_detection"] or r["above_primary_threshold"]:
                W(f"| {r['unit']} | {r['len_primary']} / {r['len_creilly']} | {r['S_primary']:.4f} | {r['S']:.4f} | "
                  f"{r['threshold_primary']:.4f} | {'yes' if r['above_primary_threshold'] else 'no'}"
                  f"{'' if r['primary_detection'] else ' (primary negative: not a detection)'} |")
        W("")
        for r in cr:
            if r["stage"] in ("J2", "J3"):
                W(f"- {r['stage']} {r['test']}: pscore creilly {r['pscore']:.4f} vs primary {r['pscore_primary']:.4f}, "
                  f"threshold {r['threshold_primary']:.4f}: {'above' if r['above_primary_threshold'] else 'not above'} "
                  f"(primary {'detection' if r['primary_detection'] else 'negative'}); letters {r['letters_primary']} / {r['letters_creilly']}.")
        W("")
    W("## What these records do not establish\n")
    W("- No detection here is a reading. Each needs check- reproduction from key and edits alone, and "
      "the adversary failing to equal its score with the same freedom.")
    W("- Novelty is not assessed. creilly, 0wwafa or Lasry et al. may hold these plaintexts; a lit- check "
      "comes first.")
    W("- The creilly comparison uses the primary thresholds at primary lengths, so it is approximate "
      "where the lengths differ.")
    W("- J2 and J3 found width 22 (the widest searched) in every run, and so did most null draws. Both "
      "of their detections are margins of under 0.005 with no German in the plaintext.")
    W("")
    # trials factor
    TL = [json.loads(l) for l in open(os.path.join(RES, "adfgvx-trials.log"))]
    c = Counter(t["step"] for t in TL)
    W("## Trials factor (from results/adfgvx-trials.log)\n")
    for k in sorted(c):
        W(f"- {k}: {c[k]} log lines" + (f", {sum(t.get('runs', 0) for t in TL if t['step'] == k)} key runs"
                                        if any('runs' in t for t in TL if t['step'] == k) else ""))
    open(os.path.join(RES, "adfgvx-J.md"), "w").write("\n".join(L) + "\n")
    print("wrote results/adfgvx-J.md")



if __name__ == "__main__":
    step = sys.argv[1]
    sharing.be_nice()
    if step == "j0":
        run_j0()
    elif step in ("j1-null-a", "j1-null-b"):
        run_j1_null(step[-1])
    elif step == "j1-controls":
        run_j1_controls()
    elif step == "j1-targets":
        run_j1_targets()
    elif step in ("j2-null", "j3-null"):
        run_group_null(step[:2])
    elif step in ("j2-run", "j3-run"):
        run_group_tests(step[:2])
    elif step == "creilly":
        run_creilly()
    elif step == "report":
        run_report()
    else:
        sys.exit(f"unknown step {step}")
