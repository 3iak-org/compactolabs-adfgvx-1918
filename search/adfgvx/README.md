# search/adfgvx: comp-adfgvx

Written 2026-10-31 from the cipher's definition. It does not read creilly's or 0wwafa's code.

| file | what |
|---|---|
| `engine.py` | ADFGVX encrypt/decrypt (6x6 square + irregular columnar transposition; `?` square cells, `-` lost symbols, `*` wildcards) |
| `align.py` | minimal edit alignment, with the count of optimal alignments and the [min, max] of each edit type over all of them |
| `edcost.c` | an independent C cost-only edit distance, and the fitting alignment of the duplicate screen. It cross-checks `align.py` on every census message, and does the E6 and planted-control loops fast. Built into `$TMPDIR` on first use |
| `build_corpus.py` | derived corpus tables and the Schmeh-vs-creilly diff |
| `census.py` | the mutilation census, header-count check, survivorship comparison, transcription-vs-reception split, repeated receptions |
| `validate.py` | the engine re-decrypts every solved entry; corrupted inputs; planted-edit recovery |
| `plant.py` | planted-control generator (CLI and library): random or named key, census-drawn or explicit edits, extra E5 rate, E6, full truth record per control |
| `headers.py` | OCR-tolerant header parser (call signs, time, date candidates) |
| `clusters.py` | header-only clustering of the unread entries, calibrated on the solved ones |
| `periods.py` | key periods derived from the solved entries (robust page/heading ranges), the assignment rule |
| `duplicates.py` | decryption-free duplicate screen: fitting alignment, pair-level null binned by length, calibration, planted copies |
| `rdecrypt.py` | strand R plain decrypts (R1 p.153 pair, R2 p.176 "2305" with its 20-symbol gap) |
| `run_all.sh` | regenerates everything; checks the input sha256s first (`inputs.sha256`) |

No key search or solver has been run on any unread entry.

Example control:

    ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/plant.py --n 3 --seed 7 \
        --len 176 --width 20 --edits census --e5-rate 0.0066 --out $TMPDIR/c.jsonl
