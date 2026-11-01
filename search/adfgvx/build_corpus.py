"""Build the derived corpus tables and the Schmeh-vs-creilly transcription diff.

    ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/build_corpus.py

Inputs (all committed, sha256 in ciphertexts/README.md):
  ciphertexts/adfgvx-1918-log.records.json   creilly11235/adfgvx-1918 @ e60da03, data/records.json
  ciphertexts/adfgvx-1918-log.keys.json      same commit, data/keys.json
  ciphertexts/adfgvx-1918-open.txt           Schmeh 2017 list (lead's copy; read only)
Outputs:
  ciphertexts/adfgvx-1918-log.tsv            one row per log entry, header fields + symbols
  ciphertexts/adfgvx-1918-log.keys.tsv       one row per key
  ciphertexts/adfgvx-1918-log.plaintexts.tsv one row per entry with a plaintext
  results/adfgvx-transcription-diff.md       every disagreement Schmeh vs creilly
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
from align import align, plain_pair  # noqa: E402
from provenance import header as prov_header  # noqa: E402

CT = os.path.join(ROOT, "ciphertexts")
LETTERS = set("ADFGVX")
DASHES = set("-–—")

LASRY_IDS = ["sep19", "oct04", "oct28", "nov01", "nov04", "nov07", "nov10", "nov13_20",
             "nov13_16", "nov16", "nov19", "nov22", "nov25", "nov28"]
# The "16 known keys" of the brief = Lasry's 14 + the CHI key + TRUPPENVERSCHIEBUNG.
# In creilly's keys.json those two are chi_2017_comments and dec09_history (the key that reads
# Childs p.217 = Schmeh "Page 217").
SIXTEEN = LASRY_IDS + ["chi_2017_comments", "dec09_history"]


def load():
    rec = json.load(open(os.path.join(CT, "adfgvx-1918-log.records.json")))
    keys = json.load(open(os.path.join(CT, "adfgvx-1918-log.keys.json")))
    return rec, keys


def parse_schmeh(path):
    """Return list of dicts: label, page, tokens (raw), slots (normalised string), notes."""
    out = []
    cur = None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#") or not line.strip():
            continue
        if line.startswith("Page"):
            cur = {"label": line.strip(), "lines": []}
            out.append(cur)
            continue
        if cur is None:
            continue
        cur["lines"].append(line)
    for m in out:
        toks = " ".join(m["lines"]).split()
        slots = []
        notes = []
        for ti, tok in enumerate(toks):
            last = ti == len(toks) - 1
            br = tok[0] in "({" and tok[-1] in ")}"
            core = tok[1:-1] if br else tok
            if br:
                notes.append(f"group {ti+1} '{tok}' bracketed in the list (kept as 5 symbols)")
            if any(c.islower() for c in core):
                notes.append(f"group {ti+1} '{tok}' has lower case, read as upper case")
            core = core.upper()
            bad = [c for c in core if c not in LETTERS and c not in DASHES]
            if bad:
                notes.append(f"group {ti+1} '{tok}' has unexpected characters {bad}")
            nlet = sum(c in LETTERS for c in core)
            ndash_chars = sum(c in DASHES for c in core)
            if ndash_chars == 0:
                slots.append(core)
                continue
            if not last:
                nd = 5 - nlet
                if nd < ndash_chars:
                    nd = ndash_chars
                    notes.append(f"group {ti+1} '{tok}' has more dash characters than free slots")
            else:
                nd = ndash_chars
                notes.append(f"group {ti+1} '{tok}' is the final group: {nd} lost slot(s) "
                             "assumed, one per dash character (UNCERTAIN)")
            # place the lost slots where the dash characters are, spreading the extra slots
            # onto the first dash character
            s = []
            first = True
            for c in core:
                if c in LETTERS:
                    s.append(c)
                else:
                    if first:
                        s.append("-" * (nd - ndash_chars + 1))
                        first = False
                    else:
                        s.append("-")
            slots.append("".join(s))
        m["tokens"] = toks
        m["groups"] = slots
        m["slots"] = "".join(slots)
        m["notes"] = notes
        lab = m["label"].split()[1] if len(m["label"].split()) > 1 else ""
        m["page"] = int(lab) if lab.isdigit() else None
    return out


def letters_only(s):
    return "".join(c for c in s if c in LETTERS)


def tsv_escape(s):
    return ("" if s is None else str(s)).replace("\t", " ").replace("\n", " ")


def write_tables(rec, keys):
    p = os.path.join(CT, "adfgvx-1918-log.tsv")
    cols = ["id", "childs_page", "pdf_page", "page_date", "header", "part", "status", "key",
            "count_in_log", "symbols_in_log", "n_slots", "n_letters", "n_lost", "printed"]
    with open(p, "w") as f:
        f.write(prov_header("#", "search/adfgvx/build_corpus.py"))
        f.write("# Derived from ciphertexts/adfgvx-1918-log.records.json (creilly11235/adfgvx-1918 "
                "@ e60da03). page_date = the date of the Childs log page the entry is filed under "
                "(records.json 'date'); header = OCR of the entry's own header line, verbatim. "
                "printed = the log symbols as transcribed ('-' = a slot the log shows as lost). "
                "n_slots = len(printed), n_letters = ADFGVX letters, n_lost = '-' slots.\n")
        f.write("\t".join(cols) + "\n")
        for e in rec:
            pr = e["printed"] or ""
            row = [e["id"], e["childs_page"], e["pdf_page"], e["date"], e["header"], e["part"],
                   e["status"], e["key"], e["count_in_log"], e["symbols_in_log"], len(pr),
                   len(letters_only(pr)), pr.count("-"), pr]
            f.write("\t".join(tsv_escape(x) for x in row) + "\n")
    p = os.path.join(CT, "adfgvx-1918-log.keys.tsv")
    with open(p, "w") as f:
        f.write(prov_header("#", "search/adfgvx/build_corpus.py"))
        f.write("# Derived from ciphertexts/adfgvx-1918-log.keys.json (creilly @ e60da03). "
                "square: 36 cells row-major, rows/cols ADFGVX, '?' = cell blank in the source. "
                "transposition: column numbers left to right, column 1 read first. "
                "in_16 = one of the 16 keys of 0wwafa PAPER 5.3 (Lasry's 14 + CHI + "
                "TRUPPENVERSCHIEBUNG).\n")
        f.write("id\tsource\tperiod\twidth\tblank_cells\tin_lasry_2017\tin_16\ttransposition\tsquare\n")
        for k in keys:
            f.write("\t".join(tsv_escape(x) for x in [
                k["id"], k["source"], k["period"], k["width"], k["square"].count("?"),
                k["id"] in LASRY_IDS, k["id"] in SIXTEEN,
                " ".join(map(str, k["transposition"])), k["square"]]) + "\n")
    p = os.path.join(CT, "adfgvx-1918-log.plaintexts.tsv")
    with open(p, "w") as f:
        f.write(prov_header("#", "search/adfgvx/build_corpus.py"))
        f.write("# Derived from records.json (creilly @ e60da03). These are creilly's own 2026 "
                "decryptions under the named key (Lasry et al. 2017 published keys and totals, "
                "not per-entry plaintexts). Marks in plaintext: '-' unknown letter (lost "
                "symbol), '?' cell blank in the square, '#' a digit cell, '_' open position.\n")
        f.write("id\tkey\tstatus\tmethod\tconfidence\tplaintext\n")
        for e in rec:
            if e["plaintext"]:
                f.write("\t".join(tsv_escape(x) for x in [
                    e["id"], e["key"], e["status"], e["method"], e["confidence"],
                    e["plaintext"]]) + "\n")


def schmeh_diff(rec):
    sch = parse_schmeh(os.path.join(CT, "adfgvx-1918-open.txt"))
    crl = json.load(open(os.path.join(CT, "..", "ciphertexts", "adfgvx-1918-log.records.json")))
    mapping_file = None  # creilly's own schmeh_list.json is NOT used for matching
    lines = []
    W = lines.append
    W("# ADFGVX 1918: Schmeh's 2017 list against the creilly transcription of Childs's log\n")
    W(prov_header("", "search/adfgvx/build_corpus.py",
                  "transcriptions: BOTH Schmeh 2017 (ciphertexts/adfgvx-1918-open.txt) and "
                  "creilly11235/adfgvx-1918 @ e60da03 (field `printed`)"))
    W("Schmeh side: `ciphertexts/adfgvx-1918-open.txt` (sha256 9362c3d2...df94), 22 entries. "
      "Log side: `printed` field of `ciphertexts/adfgvx-1918-log.records.json` "
      "(creilly11235/adfgvx-1918 @ e60da03).\n")
    W("**Normalisation of the Schmeh text (stated, not hidden).** Groups split on white space. "
      "A group containing dash characters (-, en dash, em dash) and not the last group of its "
      "entry is taken to hold 5 slots, the missing ones lost ('-'). The last group's dashes count "
      "one slot each (uncertain). Lower case is read as upper case. Bracketed groups `( )` `{ }` "
      "are kept as 5 symbols. Every such case is listed under its entry.\n")
    W("**Matching.** Each Schmeh entry is matched to the log record, among those with the same "
      "Childs page (any page for 'Page ??' / 'Page ???'), with the least edit distance between "
      "the ADFGVX-letter strings. creilly's own matching file was not used; the result is "
      "compared with the ids it names at the end.\n")
    W("**Diff.** Unit-cost alignment of the two slot strings ('-' is a symbol). Every move that is "
      "not a match is listed. Where several minimal alignments exist the count is given, and the "
      "listed one is the canonical one (substitution preferred, then deletion, then insertion). "
      "Positions are 1-based slot positions on each side, with the 5-group number of the "
      "Schmeh side.\n")
    summary = []
    for m in sch:
        S = m["slots"]
        cands = [e for e in rec if e["printed"] and (m["page"] is None or e["childs_page"] == m["page"])]
        best = None
        for e in cands:
            a = align(letters_only(e["printed"]), letters_only(S), plain_pair)
            # cheap: only cost needed; align computes all, fine at this size
            if best is None or a["cost"] < best[0]:
                best = (a["cost"], e)
        e = best[1]
        C = e["printed"]
        a = align(C, S, plain_pair)
        diffs = [op for op in a["ops"] if op[0] != "match"]
        summary.append((m["label"], e["id"], e["status"], len(S), len(C), a["cost"],
                        a["n_optimal"], best[0]))
        W(f"\n## {m['label']} -> `{e['id']}` ({e['status']})\n")
        W(f"- Schmeh: {len(S)} slots ({len(letters_only(S))} letters, {S.count('-')} lost). "
          f"Log: {len(C)} slots ({len(letters_only(C))} letters, {C.count('-')} lost).")
        W(f"- Letter-string edit distance {best[0]}; slot-string edit distance {a['cost']} "
          f"({a['n_optimal']} minimal alignment(s)).")
        for n_ in m["notes"]:
            W(f"- Normalisation: {n_}")
        if diffs:
            W("\n| # | type | log pos | log | Schmeh pos | Schmeh group | Schmeh |")
            W("|---|---|---|---|---|---|---|")
            for k, (ty, i, j) in enumerate(diffs, 1):
                if ty == "sub":
                    W(f"| {k} | substitution | {i+1} | {C[i]} | {j+1} | {j//5+1} | {S[j]} |")
                elif ty == "del":
                    W(f"| {k} | in log only | {i+1} | {C[i]} | (after {j}) | {max(j-1,0)//5+1} | |")
                else:
                    W(f"| {k} | in Schmeh only | (after {i}) | | {j+1} | {j//5+1} | {S[j]} |")
        else:
            W("- No disagreement.")
    W("\n## Summary\n")
    W("| Schmeh entry | log id | log status | Schmeh slots | log slots | slot edits | minimal alignments | letter edits |")
    W("|---|---|---|---|---|---|---|---|")
    for s in summary:
        W("| " + " | ".join(str(x) for x in s) + " |")
    return "\n".join(lines) + "\n", summary


def main():
    rec, keys = load()
    write_tables(rec, keys)
    md, summary = schmeh_diff(rec)
    open(os.path.join(ROOT, "results", "adfgvx-transcription-diff.md"), "w").write(md)
    for s in summary:
        print(s)


if __name__ == "__main__":
    main()
