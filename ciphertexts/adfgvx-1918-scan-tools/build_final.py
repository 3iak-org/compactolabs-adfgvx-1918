"""Assemble ciphertexts/adfgvx-1918-scan-transcription.json: our reading of every target id,
the creilly comparison and its adjudication, calibration score and record anomalies.

usage: build_final.py REPO
Reads: the blind file, the worklist, the creilly records (printed, header), the raw/ adjudication
artefacts. Our readings are the blind pass unchanged: no adjudication against creilly found a
symbol where creilly was right and the blind pass wrong (see the .md).
"""
import json, sys, os, re, collections
repo = sys.argv[1]
J = lambda p: json.load(open(os.path.join(repo, p)))
B = J("ciphertexts/adfgvx-1918-scan-blind.json"); W = J("ciphertexts/adfgvx-1918-scan-worklist.json")
R = {r["id"]: r for r in J("ciphertexts/adfgvx-1918-log.records.json")}
raw = "ciphertexts/adfgvx-1918-scan-raw/"
FD = J(raw + "crosscheck/final_diff_vs_creilly.json"); IT = J(raw + "creilly-adjudication/items.json")
V = J(raw + "creilly-adjudication/verdicts.json"); C = J(raw + "creilly-adjudication/categories.json")
CAL = J(raw + "crosscheck/calibration_score.json"); OV = J("ciphertexts/adfgvx-1918-scan-mapping-overrides.json")
cat_of = {i: k for k, v in C.items() if k != "_doc" for i in v}
blocks = {(p["pdf_page"], b["block_index"]): (p, b) for p in B["pages"] for b in p["blocks"]}

MONTHS = {m: i for i, m in enumerate(["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST",
                                       "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"], 1)}
def date_of(s):
    if not s: return None
    m = re.search(r"(\d{1,2})\s*(?:st|nd|rd|th|d)?[\s.,]*([A-Za-z]{3,})", s)
    if not m: return None
    mo = [v for k, v in MONTHS.items() if k.startswith(m.group(2).upper()[:3])]
    return (int(m.group(1)), mo[0]) if mo else None
def heading_date(h):
    m = re.search(r"([A-Za-z]{3,})\s+(\d{1,2})\s*(?:st|nd|rd|th|d)", h or "")
    if not m: return None
    mo = [v for k, v in MONTHS.items() if k.startswith(m.group(1).upper()[:3])]
    return (int(m.group(2)), mo[0]) if mo else None
def net_indicator(label):
    """The call/net indicator as printed in the block label, e.g. 'RICHI-240', 'CHI-170', 'RIZI-46',
    'RICHI-----' (count typed as dashes), 'Richi-408'; None if the label has none."""
    m = [x.strip() for x in re.findall(r"((?:RI\s?)?(?:CHI|ZI)\s*[-\u2013]*\s*[0-9?\-]*)", label or "", re.I)]
    return " / ".join(m) if m else None
def net(label):
    l = (label or "").upper().replace(" ", "")
    for n in ("RICHI", "RIZI", "CHI"):
        if n in l: return n
    return None

entries = {}; tallies = {"unsolved": collections.Counter(), "calibration": collections.Counter()}
for sset in ("unsolved", "calibration"):
    for t in W[sset]:
        rid = t["id"]; f = FD[rid]; r = R[rid]
        spans = f["spans"]
        bl = [blocks[(s[0], s[1])] for s in spans]
        items = [dict(idx=x["idx"], category=cat_of[x["idx"]], verdict=V[str(x["idx"])]["verdict"], note=V[str(x["idx"])]["note"],
                      page=x["page"], block=x["block"], lines=x["lines"], ops=x["ops"], ours_ctx=x["ours_ctx"], theirs_ctx=x["theirs_ctx"])
                 for x in IT if x["id"] == rid]
        cols = collections.Counter()
        for x in items:
            cols[x["category"]] += len(x["ops"]); tallies[sset][x["category"]] += len(x["ops"])
        unc = []; adj = []; notes = []
        for p, b in bl:
            unc += [dict(page=p["pdf_page"], block=b["block_index"], **u) for u in b.get("uncertain", [])]
            adj += [dict(page=p["pdf_page"], block=b["block_index"], **a) for a in b.get("adjudications", [])]
            if b.get("notes"): notes.append(f'p{p["pdf_page"]} b{b["block_index"]}: {b["notes"]}')
        p0, b0 = bl[0] if bl else (None, None)
        hd = heading_date(b0["heading"]) if b0 else None; pd = date_of(p0["page_date_line"]) if p0 else None
        entries[rid] = dict(
            set=sset, creilly_status=r["status"], pdf_page=t["pdf_page"], childs_page=t["childs_page"],
            spans=spans, mapping=f["mapping"], mapping_override=OV.get(rid, {}).get("reason"),
            heading=b0["heading"] if b0 else None, preamble=b0.get("preamble") if b0 else None,
            label=[b["label"] for _, b in bl], net=[net(b["label"]) for _, b in bl],
            net_indicator=[net_indicator(b["label"]) for _, b in bl],
            header_count=[b.get("count") for _, b in bl],
            lines=[l for _, b in bl for l in b["lines"]] if len(spans) != 1 or (spans[0][2] == 0 and spans[0][3] == bl[0][1]["n_symbols"]) else None,
            symbols=f["ours"], n_symbols=f["n_ours"],
            n_lost=f["ours"].count("-"), n_unread=f["ours"].count("?"),
            non_adfgvx=sorted({c for c in f["ours"] if c.isalpha() and c not in "ADFGVX"}),
            page_date_line=p0["page_date_line"] if p0 else None, heading_date=hd, page_date=pd,
            heading_date_differs_from_page=(hd is not None and pd is not None and hd != pd),
            creilly_printed=f["theirs"], creilly_header=r["header"],
            blind_vs_creilly=dict(columns=f["columns"], equal=f["equal"], edit_distance=f["edit_distance"], by_category=dict(cols)),
            adjudication=items, reader_uncertain=unc, ocr_reader_adjudications=adj, reader_notes=notes,
            coverage=dict(ocr_checked_symbols=sum(b["coverage"]["ocr_checked_symbols"] for _, b in bl),
                          reader2_checked_symbols=sum(b["coverage"]["reader2_checked_symbols"] for _, b in bl),
                          block_symbols=sum(b["n_symbols"] for _, b in bl)))
        if sset == "calibration":
            entries[rid]["calibration"] = CAL["entries"][rid]

doc = dict(meta=dict(B["meta"], what="Independent reading of the 83 Unsolved entries and 30 calibration entries of creilly's records, from the scan; blind pass + adjudication against creilly",
                     blind_pass_file="ciphertexts/adfgvx-1918-scan-blind.json", blind_pass_commit="95ceb080f9d5ccdffa9adc127650db03d934a599 (tag transcribe-adfgvx-blind-pass; 1e3a3a4 after rebase onto lead-adfgvx, identical content)",
                     creilly_source="ciphertexts/adfgvx-1918-log.records.json (creilly11235/adfgvx-1918 @ e60da03)",
                     ladder="single transcriber (one reading team, one adjudicator): NOT [C]. Counts are exact counts of this reading; error rates are [S] on the calibration sample."),
           tallies={k: dict(v) for k, v in tallies.items()}, calibration_total=CAL["total"], entries=entries)
json.dump(doc, open(os.path.join(repo, "ciphertexts/adfgvx-1918-scan-transcription.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(doc["tallies"], indent=1)); print(CAL["total"])
