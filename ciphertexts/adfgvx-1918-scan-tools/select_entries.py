"""Write the blind work list: the 83 Unsolved entries plus the calibration set.

Reads ONLY id, childs_page, pdf_page, date, header, part, status and method from
creilly's records.json. It never reads or prints a symbol field.

Calibration rule (fixed 2026-10-31 before any calibration entry was viewed):
  candidates = records with status == "Solved" and method == "period key, as transcribed"
  (the trivial method: creilly's log transcription decrypts as it stands),
  sorted by (pdf_page, id); take candidates[floor(i * N / 30)] for i = 0..29.
"""
import json, sys

src, out = sys.argv[1], sys.argv[2]
recs = json.load(open(src))
keep = ("id", "childs_page", "pdf_page", "date", "header", "part")
unsolved = [{k: r[k] for k in keep} | {"set": "unsolved"} for r in recs if r["status"] == "Unsolved"]
cand = sorted((r for r in recs if r["status"] == "Solved" and r["method"] == "period key, as transcribed"),
              key=lambda r: (r["pdf_page"], r["id"]))
N = len(cand)
cal = [{k: cand[(i * N) // 30][k] for k in keep} | {"set": "calibration"} for i in range(30)]
json.dump({"n_candidates": N, "unsolved": unsolved, "calibration": cal}, open(out, "w"), indent=1, ensure_ascii=False)
print(len(unsolved), "unsolved;", len(cal), "calibration from", N, "candidates")
