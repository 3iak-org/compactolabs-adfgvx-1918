#!/bin/bash
# Re-run everything in REPORT.md.  PY = the project venv.  Needs, in $TMPDIR:
#   creilly/  (git clone https://github.com/creilly11235/adfgvx-1918 ; git checkout e60da03)
#   wwafa/    (git clone https://github.com/0wwafa/adfgvx-1918)           [only PAPER.md/issue are read]
#   corpus/pg<id>.txt for the ids in german.py (https://www.gutenberg.org/cache/epub/<id>/pg<id>.txt)
# Run from this directory.  Long steps are marked (long).
PY=~/dev/projects/ciphers/.venv/bin/python
OUT=${TMPDIR:-/tmp}/out; mkdir -p $OUT results
# every shared object any script loads (alcost: census.py; libkern: kern.py; libsw: r34.py; libtsearch: tsearch.py;
# libgap: gapscan.py; liblev: r34_prereg.py)
for pair in alcost:alcost libkern:kern libsw:sw libtsearch:tsearch libgap:gapscan liblev:lev; do
  gcc -O2 -shared -fPIC -o ${pair%%:*}.so ${pair##*:}.c || exit 1
done
$PY step0_validate.py                       # task 0
$PY census.py printed                       # census (~70 s); writes census_printed.json
$PY census_report.py printed                # tables + results/census_check_printed.tsv
# comparison with comp (only after the census above is committed): git show origin/agent/comp-adfgvx:results/adfgvx-mutilation.csv > $OUT/comp.csv
#   $PY census_compare.py $OUT/comp.csv ; $PY census_lev.py $OUT/comp.csv
$PY r1_repro.py                             # R1 reproduction from key + claimed square, round trip
$PY r1_part6.py                             # R1 free-square re-derivation (part 5 alone, joint)
$PY r1_null.py calib                        # optimiser saturation on the claim
$PY r1_null.py nulls 736 100 20 $OUT/r1_a.jsonl   # (long) 16 claim + 736 random keys + 736 shuffles + 153 swaps; reported run used 736 random keys, 486 shuffles
$PY r1_null.py swaps 100 20 $OUT/r1_swaps.jsonl
$PY r1_null.py sat $OUT/r1_sat.json         # (long) 48 random keys at 400x40
$PY r1_analyse.py results/r1_nulls_all.jsonl
$PY r2.py                                   # R2 reproduction
$PY r2_null.py $OUT/r2_scan.json            # (long) 21 keys x 221 gap positions x 2 scorers x 2 modes
$PY r2_null2.py 200 $OUT/r2_null2.json      # (long) random keys / shuffles / cross squares
$PY r2_analyse.py $OUT/r2_scan.json $OUT/r2_null2.json
$PY r34.py                                  # R3/R4 Smith-Waterman vs all entries + shuffle nulls
$PY r34_detail.py results/r34_detail.json   # alignments, chance, decrypt under the solved key

# ---- prereg-compliant strand R (v2) ----
$PY decoys_r1.py                                        # committed at f821aa8 BEFORE any decoy was scored
$PY transcr_compare.py > results/transcr_compare.txt   # creilly vs Schmeh; R1 square vs 21 known squares
$PY r2_prereg.py claim results/r2_prereg_claim.json     # R2 masked scan, TEL + LIT
$PY r2_prereg.py solved results/r2_prereg_solved.json   # R2 solved-entry null (58 entries x 21 wrong keys)
$PY r34_prereg.py results/r34_prereg.json               # R3/R4 statistics vs all solved entries, both transcriptions
$PY r1_run.py $OUT/r1_prereg.jsonl 60                   # (long, ~1 h on a loaded box) R1 search-family null
$PY r1_prereg_analyse.py results/r1_prereg.jsonl
$PY r2_rules.py results/r2_rules.json                   # R2 '?'-rule rows (mask headline / digit / complete-only), TEL+LIT
$PY r1_fixed.py $OUT/r1_fixed.json 100                  # R1 fixed-key rows
$PY r_schmeh_rerun.py                                   # B4 + C4 comparison with comp's plain decrypts
