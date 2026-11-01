# Blind visual transcription protocol (ADFGVX log, Childs Appendix B scan)

You are transcribing typewritten ADFGVX cipher groups from page images of a 1918 radio
intercept log. Your reading must be INDEPENDENT: it will be compared later against another
person's transcription, and the comparison is worthless if you have seen theirs.

## Hard rules
- Do NOT open, grep, cat or list anything under the repo directories `ciphertexts/` (except
  running the tool `ciphertexts/adfgvx-1918-scan-tools/crop.py`), `search/`, `results/`,
  `verify/`, `findings/`, `master-plan/`, `literature/`, `referee/`, `adversary/`, and do not
  look anything up on the web. Your only source is the PDF.
- Do not run any decryption. Do not "correct" what is printed. Transcribe what the page shows,
  even if a group has 4 or 6 letters, even if a letter outside ADFGVX appears.
- Do not edit any file in the repo. Write only your output file.

## Tools
- PDF: /tmp/gp-scratch/ciphers/transcribe-adfgvx/pdf/childs.pdf (248 pages, 300 dpi scans,
  page size 2409 x 3437 px).
- Crop to PNG, then view the PNG with the Read tool:
  ~/dev/projects/ciphers/.venv/bin/python -I \
    ~/dev/projects/.sessions/ciphers/transcribe-adfgvx/ciphertexts/adfgvx-1918-scan-tools/crop.py \
    /tmp/gp-scratch/ciphers/transcribe-adfgvx/pdf/childs.pdf PAGE OUT.png x0 y0 x1 y1 [--scale S]
  Coordinates are fractions of the page (0..1) or pixels (>1). With no box, the whole page.
  Write PNGs into your own directory /tmp/gp-scratch/ciphers/transcribe-adfgvx/vis/aK/ (K = your
  agent number).
- Recommended: first view the whole page with --scale 0.35 to see the layout (headings, blocks,
  where lines are). Then read in strips of AT MOST ~6 printed lines, full text width
  (x from about 0.03 to 0.97), at native scale (--scale 1). Strips should overlap a little;
  make sure each printed line is transcribed exactly once (use the left label / first group to
  anchor). For any group you are unsure of, crop just that group at --scale 2 or 3 and look again.

## What to record
Transcribe EVERY cipher block on each of your pages, in the order they appear top to bottom.
A "block" is one run of cipher groups with its own left-hand label (e.g. `RICHI-220`, or
`1 TL` / `RICHI-330`, or `2 TL RICHI-66`); a multi-part message ("1 TL", "2 TL", ...) gives one
block per part. If a block continues onto the next PDF page, follow it there and finish it (mark
`continues_on_next_page`). If the top of one of your pages continues a block from the previous
page, transcribe that continuation as its own block with `continued_from_previous_page: true`.

Output: ONE JSON file /tmp/gp-scratch/ciphers/transcribe-adfgvx/vis/agentK.json :
{
 "agent": K,
 "pages": [
  {"pdf_page": 72,
   "page_date_line": "5th OCTOBER, 1918.",          // the date line at the top, as printed, or ""
   "blocks": [
    {"block_index": 0,                               // 0-based order on this page
     "heading": "A) NKJ v ---  (---- October 11th)",  // the lettered heading this block sits under, exactly as printed
     "preamble": ["NR 44 0628 (5.10)"],               // printed lines between heading and groups (NR..., FUER..., etc.)
     "label": "RICHI-220",                            // left-hand text of the block, all of it, e.g. "1 TL RICHI-330"
     "part": null,                                    // the TL number if labelled "n TL", else null
     "count": 220,                                    // the number in the label (header symbol count), null if none / unreadable
     "lines": ["VDGVF GDVFF GAGGF AFVDD DFFGF DFAGF VVGVF FGGFV",
               "DADFF XFVVX ..."],
     "continued_from_previous_page": false,
     "continues_on_next_page": false,
     "uncertain": [{"line": 1, "group": 2, "read": "XFGAG", "alt": "X?GAG", "why": "smudge over 2nd letter"}],
     "notes": ""                                      // anything odd: handwriting, overstrike, a second message apparently run into this block, text outside the grid
    }]
  }]
}
Conventions inside `lines`:
- One string per PRINTED line; groups separated by ONE space, exactly as the page divides them.
- Letters as printed (normally A D F G V X). Keep parentheses exactly: `F(X)DFA`, `FDX(X)-`.
- `-` for each dash printed in the groups (a lost symbol as the log prints it).
- `?` for a symbol you cannot read at all. If you can read it but are unsure, write your best
  reading in `lines` and add an entry to `uncertain` (line and group are 0-based).
- If you see any other mark (a dot, a handwritten letter, a strike-through), write your best
  reading and describe it in `notes`.
Accuracy matters far more than speed: the result is a calibrated transcription. Common
confusions on this typeface are D/G, F/P, V/X, A/4, and skipped or doubled groups at strip
boundaries — check group counts per line against the image.

Write the JSON incrementally (rewrite the file after each page) so partial work survives.
When finished, reply with: pages done, number of blocks, total symbols, and every page/block
where you were unsure or noticed something odd.
