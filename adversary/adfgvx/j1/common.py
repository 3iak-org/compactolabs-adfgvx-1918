"""adv-adfgvx J1 attack: shared inputs (read-only copies of the claim's frozen inputs)."""
import json, os, subprocess, ast
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("J1SRC", os.path.join(os.environ.get("TMPDIR", "/tmp"), "lead"))  # git archive of lead-adfgvx c9e554a
LMT = os.environ.get("J1LM", os.path.join(os.environ.get("TMPDIR", "/tmp"), "lm.tab"))   # sha256 675a65d4...
E2 = os.environ.get("J1E2", os.path.join(os.environ.get("TMPDIR", "/tmp"), "e2"))

def keys():
    return {k["id"]: k for k in json.load(open(os.path.join(SRC, "ciphertexts/adfgvx-1918-log.keys.json")))}

def units():
    J = json.load(open(os.path.join(SRC, "results/adfgvx-J0.json")))
    return {r["unit"]: r for r in J["rows"]}

def targets():
    out = []
    for l in open(os.path.join(SRC, "results/adfgvx-J1-targets.jsonl")):
        d = json.loads(l)
        if not d.get("meta"):
            out.append(d)
    return out

def job(tag, square, perm, text):
    return f"{tag} {square} {len(perm)} {' '.join(map(str, perm))} {text}\n"

def run(jobs):
    p = subprocess.run([E2, LMT, os.environ.get("J1CAP", "2")], input="".join(jobs), capture_output=True, text=True, check=True)
    res = {}
    for l in p.stdout.splitlines():
        tag, best, s0, ed, pl = l.split(" ")
        res[tag] = dict(score=float(best), score0=float(s0), edits="" if ed == "-" else ed, plain=pl)
    return res
