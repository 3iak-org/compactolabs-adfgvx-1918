"""Parse Schmeh-2017 transcription (ciphertexts/adfgvx-1918-open.txt on lead-adfgvx; sha256 9362c3d2...df94).
Dash rule (verified against the 5-slot groups): '-' = 1 lost symbol, en dash = 2, em dash = 3.  Lowercase letter
= uncertain reading (kept as the uppercase symbol in variant 'upper', as lost in variant 'lost')."""
import subprocess, hashlib, re
def raw():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(here, "data_snapshots", "adfgvx-1918-open.txt"), os.path.join(here, "..", "..", "ciphertexts", "adfgvx-1918-open.txt")):
        if os.path.exists(p): return open(p, encoding="utf-8").read()
    return subprocess.check_output(["git", "show", "origin/lead-adfgvx:ciphertexts/adfgvx-1918-open.txt"], cwd=here).decode()
def entries(variant="upper"):
    t = raw(); out = []; cur = None
    for line in t.splitlines():
        if line.startswith("#") or not line.strip(): continue
        m = re.match(r"Page (\S+)", line)
        if m: cur = [line.strip(), ""]; out.append(cur); continue
        if cur is None: continue
        cur[1] += " " + line.strip()
    res = []
    for head, body in out:
        s = ""
        for ch in body:
            if ch in " (){}": continue
            if ch == "—": s += "---"
            elif ch == "–": s += "--"
            elif ch == "-": s += "-"
            elif ch.islower(): s += ch.upper() if variant == "upper" else "-"
            else: s += ch
        res.append((head, s))
    return res
if __name__ == "__main__":
    print(hashlib.sha256(raw().encode()).hexdigest()[:16])
    for h, s in entries(): print(h, len(s), s[:30])
