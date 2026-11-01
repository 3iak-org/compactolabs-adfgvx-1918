"""check-adfgvx-j3: decrypt the 6 nov07 members under the stated key; compare to comp's record
only AFTER computing. Run: .venv/bin/python verify/adfgvx/J3-repro.py  (from repo root)"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from adfgvx import decrypt
TR = [int(x) for x in "1 22 17 9 14 3 8 15 19 21 11 5 6 7 2 10 16 12 13 18 4 20".split()]
SQ = "PHC68O5EDQ7MBF29JWK13NL4YUZSTRAX0GVI"
M = ["p076A", "p166A", "p166A.2", "p167A", "p167A5", "p173A"]
root = os.path.join(os.path.dirname(__file__), "..", "..")
rows = {r["unit"]: r["text"] for r in json.load(open(f"{root}/results/adfgvx-J0.json"))["rows"]}
mine = {m: decrypt(rows[m], TR, SQ) for m in M}   # computed before comp's record is opened
rec = next(json.loads(l) for l in open(f"{root}/results/adfgvx-J3-runs.jsonl") if json.loads(l).get("test") == "nov07")
assert [int(x) for x in rec["trans"].split()] == TR and rec["square"] == SQ and rec["width"] == 22 and rec["members"] == M
out = ["# J3 repro: nov07 decryptions (check-adfgvx, 2026-11-01)", "",
       "Key: width 22, transposition `%s`, square `%s` (confirmed equal to the record). Code: `verify/adfgvx/adfgvx.py`; regenerate with `.venv/bin/python verify/adfgvx/J3-repro.py`. `-` = lost symbol, `?` = pair with a lost symbol.\n" % (rec["trans"], SQ),
       "| member | symbols | letters | equals comp (comp's lost-pair marker read as ?) |", "|---|---|---|---|"]
ok = True
for m in M:
    e = mine[m] == rec["plain"][m].replace("-", "?"); ok &= e  # comp writes a lost pair as "-", this code as "?"
    out.append(f"| {m} | {len(rows[m])} | {len(mine[m])} | {'YES' if e else 'NO'} |")
out += ["", "## Plaintexts (mine)", ""] + [f"- {m}: `{mine[m]}`" for m in M]
out += ["", "Note: this code marks a pair containing a lost symbol `?`; comp's record uses `-`. Compared with `-` read as `?`; no other difference.", f"**All 6 identical: {ok}.**", ""]
open(os.path.join(os.path.dirname(__file__), "J3-REPRO.md"), "w").write("\n".join(out) + "\nGerman? (my judgement, not a measurement): no. Letter salad; the 6 texts hold only German-looking fragments (EN, ER, UN, EIN, NR) at about chance level, no word or phrase, and the digits/X pattern is not number-spelling. Consistent with comp's own \"letter salad\" label.\n")
print("\n".join(out))
