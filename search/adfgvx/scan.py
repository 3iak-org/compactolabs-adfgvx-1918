"""The scan transcription of the unread entries as UNITS for strand J (comp-adfgvx, 2026-11-01).

Source: ciphertexts/adfgvx-1918-scan-transcription.json (transcribe-adfgvx; merged into
lead-adfgvx a4028ce). It is the PRIMARY transcription; creilly @ e60da03 is the secondary.

Units: one per printed cipher BLOCK, from each entry's `spans` (pdf_page, block, start, end):
  - entries sharing a block are MERGED in span order (p083B2+p083B, p101B2+p101B,
    p142A2+p142A, p153B4+p153B: creilly split one block into first line + rest);
  - an entry with two spans is SPLIT into two units (p0924 = "2 TL RICHI-290" + "3 TL RICHI-358");
  - an entry with no span is DROPPED (p220C: not ciphertext on the page).
Unit id: the creilly ids joined with '+', or the id plus '#1', '#2' for a split.

Symbol policy (proposed for the J prereg; PRIMARY reading used here):
  P1  '-' (printed lost mark) and '?' (unreadable): one lost slot.
  P2  a letter outside ADFGVX: one lost slot at its position. Alternative for W only: VV.
  P3  a parenthesised single symbol inside a group, e.g. F(X)DFA: primary = the printed symbol;
      alternative = a lost slot. (In every case here the symbol completes a 5-group.)
  P4  a whole parenthesised group, e.g. (DDAGD): primary = kept; alternative = deleted.
  P5  annotation notes ("(interference)", "(missed 20 groups)", "(Balance jammed)", "(Jm'd)"):
      no symbols. They mark a gap at a known position, of stated or unknown length. That gap is
      a pre-registered edit event of the attack, not part of the reading.
  Every alternative reading is a variant, and every variant is a trial.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCAN = os.path.join(ROOT, "ciphertexts", "adfgvx-1918-scan-transcription.json")
LET = set("ADFGVX")


def primary(sym):
    """P1 + P2 on the entry's `symbols` string (parentheses already stripped, so P3/P4 keep)."""
    return "".join(c if c in LET else "-" for c in sym)


def span_lines(entry, si):
    """The entry's `lines` that belong to span si (by cumulative symbol count; a note is
    attributed to the line, and so the block, where it is printed)."""
    lines = entry.get("lines") or []
    if len(entry.get("spans") or []) <= 1:
        return lines
    bounds, off = [], 0
    for (_, _, a, b) in entry["spans"]:
        bounds.append((off, off + b - a))
        off += b - a
    lo, hi = bounds[si]
    out, n = [], 0
    for l in lines:
        k = len(re.sub(r"\s", "", re.sub(r"\([^)]*[a-z ][^)]*\)", "", l)).replace("(", "").replace(")", ""))
        if lo <= n < hi or (k == 0 and lo <= n <= hi and si == len(bounds) - 1):
            out.append(l)
        elif k == 0 and n == lo:
            out.append(l)
        n += k
    return out


def notation(entry, si=None):
    """Count the P2-P5 items in an entry's printed lines (they set the variant count); for a
    split entry, only the lines of span si."""
    L = " ".join(entry.get("lines") or [] if si is None else span_lines(entry, si))
    return {"P2_non_adfgvx": len(entry.get("non_adfgvx") or []),
            "P3_paren_symbol": len(re.findall(r"\(([A-Z])\)", L)),
            "P4_paren_group": len(re.findall(r"(?<!\S)\([A-Z\-]{4,6}\)(?!\S)", L)),
            "P5_notes": re.findall(r"\([^)]*[a-z][^)]*\)", L)}


def units():
    d = json.load(open(SCAN))
    U = {k: v for k, v in d["entries"].items() if v["set"] == "unsolved"}
    blocks = {}
    dropped = []
    split = []
    for k, v in U.items():
        if not v["spans"]:
            dropped.append(k)
            continue
        if len(v["spans"]) > 1:
            split.append(k)
        # symbols of each span: cut the entry's symbol string by span lengths, in order
        off = 0
        for si, (pg, blk, a, b) in enumerate(v["spans"]):
            n = b - a
            part = v["symbols"][off:off + n]
            off += n
            blocks.setdefault((pg, blk), []).append((a, k, si, part, v))
    out = []
    for (pg, blk), parts in sorted(blocks.items()):
        parts.sort()
        ids = []
        for a, k, si, part, v in parts:
            ids.append(k if len(v["spans"]) == 1 else f"{k}#{si+1}")
        v0 = parts[0][4]
        si0 = parts[0][2]
        sym = "".join(p[3] for p in parts)
        net = v0["net"][si0] if v0["net"] and si0 < len(v0["net"]) else None
        hc = v0["header_count"][si0] if v0["header_count"] and si0 < len(v0["header_count"]) else None
        nota = {}
        for _, k, si, _, v in parts:
            for x, y in notation(v, si if len(v["spans"]) > 1 else None).items():
                nota[x] = nota.get(x, 0) + y if not isinstance(y, list) else nota.get(x, []) + y
        out.append({
            "unit": "+".join(dict.fromkeys(ids)), "ids": [p[1] for p in parts],
            "pdf_page": pg, "childs_page": v0["childs_page"], "block": blk,
            "heading": v0["heading"], "heading_date": v0["heading_date"],
            "page_date": v0["page_date"], "net": net, "header_count": hc,
            "printed_scan": sym, "primary": primary(sym), "notation": nota,
            "merged": len(parts) > 1, "split_from": parts[0][1] if parts[0][1] in split else None,
        })
    return out, {"dropped": dropped, "split": split,
                 "merged": [u["unit"] for u in out if u["merged"]]}


def report():
    import sys
    sys.path.insert(0, HERE)
    from provenance import header as prov_header
    us, ch = units()
    rec = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.records.json")))}
    L = []
    W = L.append
    W("# ADFGVX 1918: the scan transcription as units for strand J\n")
    W(prov_header("", "search/adfgvx/scan.py", "transcription: SCAN (ciphertexts/adfgvx-1918-scan-"
                  "transcription.json, transcribe-adfgvx, merged lead-adfgvx a4028ce); creilly @ "
                  "e60da03 for comparison"))
    W("## What was done to creilly's ids\n")
    W(f"- **Merged** (creilly split one printed block into its first line and the rest): "
      f"{', '.join(ch['merged'])}.")
    W(f"- **Split** (creilly joined two printed blocks): {', '.join(ch['split'])} -> "
      f"{', '.join(u['unit'] for u in us if u['split_from'])}.")
    W(f"- **Dropped** (not ciphertext on the page): {', '.join(ch['dropped'])}.")
    W("- **Headings, dates and nets** are the scan's readings of the page (e.g. p141B.2 is "
      "'C) UKS RAT v NKJ ... November 6th'; p076A is POT v NKJ).")
    W(f"\n{len(us)} units from {sum(len(u['ids']) for u in us)} creilly ids "
      f"(83 Unsolved ids; one dropped).\n")
    W("## Proposed symbol policy (for the J prereg to fix)\n")
    W("| rule | printed | primary reading | alternative reading(s), each a variant and so a trial |")
    W("|---|---|---|---|")
    W("| P1 | `-` lost mark, `?` unreadable | one lost slot | none |")
    W("| P2 | a letter outside ADFGVX (B C E I K N O R S T U W) | one lost slot at its position | W only: VV (two symbols; creilly's reading) |")
    W("| P3 | a parenthesised symbol inside a group, `F(X)DFA` | the printed symbol (it completes the 5-group in every case here) | a lost slot |")
    W("| P4 | a whole parenthesised group, `(DDAGD)` | kept | deleted (the operator may have flagged a repeated group, as on Schmeh's p.158) |")
    W("| P5 | a note: `(interference)`, `(missed 20 groups)`, `(Balance jammed)`, `(Jm'd)` | no symbols | a gap at the note's position: a stated length (20 groups = 100 symbols) is inserted as lost slots; an unknown length is one pre-registered gap edit whose length (0 to header count minus printed count) the attack searches, counted in the trials factor, not in the edit cap |")
    W("\nWhat the parentheses meant to Childs is not established (transcribe-adfgvx). The policy "
      "keeps the printed reading as primary and makes every alternative an explicit, counted "
      "trial, so no reading is chosen after seeing a decryption.\n")
    W("## Units with notation, and their variant counts\n")
    W("Variants = 2^(P3 + P4) x 2^(W count) for the reading alone; P5 gaps add their own length "
      "search.\n")
    W("| unit | net | header count | printed | lost slots (P1+P2) | P2 letters | P3 | P4 | P5 notes | reading variants |")
    W("|---|---|---|---|---|---|---|---|---|---|")
    tot = 1
    for u in us:
        n = u["notation"]
        w = u["printed_scan"].count("W")
        var = 2 ** (n["P3_paren_symbol"] + n["P4_paren_group"] + w)
        tot *= var
        if var > 1 or n["P2_non_adfgvx"] or n["P5_notes"] or u["merged"] or u["split_from"]:
            W(f"| {u['unit']} | {u['net']} | {u['header_count']} | {len(u['primary'])} | "
              f"{u['primary'].count('-')} | {n['P2_non_adfgvx']} | {n['P3_paren_symbol']} | "
              f"{n['P4_paren_group']} | {'; '.join(n['P5_notes'])} | {var} |")
    W(f"\nProduct of reading variants over all units: {tot}.\n")
    W("## Damage rates, scan against creilly (the power test is planted at the scan's)\n")
    P = [u["primary"] for u in us]
    C = [e["printed"] for e in rec.values() if e["status"] == "Unsolved" and e["printed"]]
    W("| transcription | entries | slots | lost slots per 100 | odd length |")
    W("|---|---|---|---|---|")
    W(f"| scan (units, primary) | {len(P)} | {sum(map(len, P))} | "
      f"{100*sum(p.count('-') for p in P)/sum(map(len, P)):.2f} | "
      f"{sum(len(p) % 2 for p in P)}/{len(P)} ({100*sum(len(p) % 2 for p in P)/len(P):.1f}%) |")
    W(f"| creilly (Unsolved ids) | {len(C)} | {sum(map(len, C))} | "
      f"{100*sum(c.count('-') for c in C)/sum(map(len, C)):.2f} | "
      f"{sum(len(c) % 2 for c in C)}/{len(C)} ({100*sum(len(c) % 2 for c in C)/len(C):.1f}%) |")
    W("\n## Anomalies left for the lead\n")
    W("- p071A1 is labelled `CHI-220` but its part 2, p071A2, prints `CHI-186 RICHI-186`. The two "
      "parts share a heading and so normally a key; the clustering puts p071A1 in the CHI group "
      "and p071A2 in oct04. Which net the message is on is not settled here.")
    W("- p0924's note `(missed 20 groups)` opens the 14th printed line (0-based index 13) of the "
      "entry's `lines`, after 5 lines of block 2: it belongs to p0924#2 only (referee H1).")
    open(os.path.join(ROOT, "results", "adfgvx-scan-units.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    report()
