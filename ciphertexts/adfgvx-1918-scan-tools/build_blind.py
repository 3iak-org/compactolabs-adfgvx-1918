"""Assemble the blind transcription from the first readers, the adjudications, and the
cross-check coverage. Reads nothing from creilly's records.

usage: build_blind.py VISDIR ADJ_DIR CMP_OCR.json CMP_READERS.json OUT.json
- lines: reader-1 lines with the adjudicated corrections applied (group-level, by
  page/block/line/group, only if the group still holds the reader's reading).
- symbols: the cipher symbols of the block in order: letters (any A-Z, as printed), '-' lost,
  '?' unreadable; parentheses dropped (the letters inside count), annotation tokens dropped.
- coverage: per block, symbols on lines that the OCR channel matched, and on lines that
  the second reader matched (the two cross-checks).
"""
import json, glob, os, re, sys, hashlib

vis_dir, adj_dir, cmp_ocr, cmp_rd, out = sys.argv[1:6]
ADFGVX = set("ADFGVX")

def is_annotation(tok):
    t = tok.replace("(", "").replace(")", "")
    if not t or any(c.islower() for c in t) or any(c.isdigit() for c in t) or "'" in t:
        return True
    if not re.fullmatch(r"[A-Z?\-]+", t):
        return True
    if len(t) >= 7 and sum(c not in ADFGVX and c not in "-?" for c in t) >= 2:
        return True     # a word such as INTERFERENCE
    return False

def symbols_of(lines):
    s = []
    for l in lines:
        for tok in l.split():
            if is_annotation(tok):
                continue
            s.append(tok.replace("(", "").replace(")", ""))
    return "".join(s)

adjs = []
for f in sorted(glob.glob(os.path.join(adj_dir, "adj_*.json"))):
    for a in json.load(open(f)):
        a["file"] = os.path.basename(f); adjs.append(a)
ocr = json.load(open(cmp_ocr)); rd = json.load(open(cmp_rd))
ocr_lines = {(x["page"], x["block"], x["line"]) for x in ocr["lines"]}
rd_unmatched = {(x["page"], x["block"], x["line"]) for x in rd["a_only_lines"]}
rd_pages = set(rd["stats"].get("page_list", []))

pages = []
for f in sorted(glob.glob(os.path.join(vis_dir, "agent*.json"))):
    for p in json.load(open(f))["pages"]:
        pages.append(p)
pages.sort(key=lambda p: p["pdf_page"])

applied = []
for p in pages:
    pg = p["pdf_page"]
    for b in p["blocks"]:
        b["lines_reader1"] = list(b["lines"])
        lines = [l.split(" ") for l in b["lines"]]
        b["adjudications"] = []
        for a in adjs:
            if (a["page"], a["block"]) != (pg, b["block_index"]):
                continue
            toks = lines[a["line"]]
            gi = [i for i, t in enumerate(toks) if not is_annotation(t)]
            g = gi[a["group"]] if a["group"] < len(gi) else None
            ok = g is not None and toks[g].replace("(", "").replace(")", "") in (a["vision"], a["final"])
            if ok and a["final"] != a["vision"]:
                toks[g] = a["final"]
            b["adjudications"].append({k: a[k] for k in ("line", "group", "vision", "other", "channel", "verdict", "final", "note")} | {"applied": ok})
            a["_ok"] = a.get("_ok", False) or ok
        b["lines"] = [" ".join(t) for t in lines]
        b["symbols"] = symbols_of(b["lines"])
        b["n_symbols"] = len(b["symbols"])
        b["n_lost"] = b["symbols"].count("-"); b["n_unread"] = b["symbols"].count("?")
        b["non_adfgvx"] = sorted({c for c in b["symbols"] if c.isalpha() and c not in ADFGVX})
        ocr_n = sum(len(symbols_of([l])) for li, l in enumerate(b["lines"]) if (pg, b["block_index"], li) in ocr_lines)
        rd_n = sum(len(symbols_of([l])) for li, l in enumerate(b["lines"]) if pg in rd_pages and (pg, b["block_index"], li) not in rd_unmatched)
        b["coverage"] = {"ocr_checked_symbols": ocr_n, "reader2_checked_symbols": rd_n}
        b["count_matches_label"] = (b.get("count") == b["n_symbols"]) if b.get("count") is not None else None
missing = [a for a in adjs if not a.get("_ok")]
doc = {"meta": {
           "what": "Blind transcription of every cipher block on 80 PDF pages of Childs, General Solution of the ADFGVX Cipher System (Aegean Park Press), Appendix B intercept log",
           "source_pdf": "Google Drive file 1_JiNMck7eUvdrOTrH7fsj1Yh44t-VSC6 via richardbean.id.au/misc/kryptos/aegean-park-press.html",
           "source_sha256": "157e41a12374c6c1f464f52f587fbf6be6e0e08706ac35f7f4b0d66dc798ad06",
           "accessed": "2026-10-31",
           "blind": "No symbol of creilly's records.json (or any other transcription) was read before this file was committed",
           "readers": "8 reader agents (readers1/) transcribed every page; 3 second readers (readers2/) re-read 24 pages independently",
           "ocr": "template OCR (ocr*.py, ocr_templates.npz) as a second channel on every page; compared group by group",
           "conventions": "lines: as printed, groups separated by one space, parentheses kept; symbols: letters as printed (any A-Z), '-' a printed lost mark, '?' unreadable; annotation tokens dropped",
           "page_numbering": "pdf_page = Childs page + 3"},
       "pages": pages, "n_blocks": sum(len(p["blocks"]) for p in pages),
       "n_symbols": sum(b["n_symbols"] for p in pages for b in p["blocks"]),
       "adjudications_total": len(adjs), "adjudications_not_applied": len(missing)}
json.dump(doc, open(out, "w"), indent=1, ensure_ascii=False)
print({k: v for k, v in doc.items() if k != "pages"})
for a in missing: print("NOT APPLIED", a)
