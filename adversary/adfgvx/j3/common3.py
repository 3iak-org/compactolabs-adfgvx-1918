"""J3 attack inputs: lead-adfgvx J0 texts and the J3 run record (git archive in $TMPDIR/lead2)."""
import json, os, subprocess, ast, math
SRC = os.environ.get("J3SRC", os.path.join(os.environ.get("TMPDIR", "/tmp"), "lead2"))
LMT = os.path.join(os.environ.get("TMPDIR", "/tmp"), "lm.tab")
A3 = os.path.join(os.environ.get("TMPDIR", "/tmp"), "a3")
FREQ = "ENRXTASIUHLOGDMCBFKZVPW102Y435J9876Q"   # J3 null meta 'freq' (training-text ranks)
def run_rec():
    for l in open(os.path.join(SRC, "results/adfgvx-J3-runs.jsonl")):
        d = json.loads(l)
        if not d.get("meta"): return d
def members():
    d = run_rec(); return ast.literal_eval(d["members"]) if isinstance(d["members"], str) else d["members"]
def texts():
    R = {r["unit"]: r for r in json.load(open(os.path.join(SRC, "results/adfgvx-J0.json")))["rows"]}
    return [R[u]["text"] for u in members()]
def a3(msgs, cmds, seed):
    job = "".join(f"MSG {t}\n" for t in msgs) + f"FREQ {FREQ}\nSEED {seed}\n" + "".join(c + "\n" for c in cmds)
    p = subprocess.run([A3, LMT], input=job, capture_output=True, text=True, check=True)
    out = []
    for l in p.stdout.splitlines():
        kind, w, sc, perm, sq, pl = l.split(" ")
        out.append(dict(kind=kind, w=int(w), score=float(sc), perm=perm, square=sq, plain=pl))
    return out
def pscore_py(msgs, square, perm):
    """independent Python decryption + J3 statistic"""
    tab = [float(x) for x in open(LMT)]; AL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"; L6 = "ADFGVX"
    k = len(perm); s = 0; P = 0; pls = []
    for v in msgs:
        n = len(v); q, r = divmod(n, k); cols = {}; pos = 0
        for rank in range(1, k + 1):
            c = perm.index(rank); ln = q + (c < r); cols[c] = v[pos:pos + ln]; pos += ln
        st = "".join(cols[c][row] for row in range(q + 1) for c in range(k) if row < len(cols[c]))
        pl = "".join(square[L6.index(st[2*j]) * 6 + L6.index(st[2*j+1])] if st[2*j] in L6 and st[2*j+1] in L6 else "-" for j in range(len(st) // 2))
        for i in range(2, len(pl)):
            t = pl[i-2:i+1]; s += math.log(1/36) if "-" in t else tab[AL.index(t[0])*1296 + AL.index(t[1])*36 + AL.index(t[2])]; P += 1
        pls.append(pl)
    return s / P, pls
