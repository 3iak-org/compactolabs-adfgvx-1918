# The open WWI ADFGVX messages of November 1918

In the autumn of 1918 Allied stations intercepted German radio traffic in the ADFGVX cipher,
between Berlin and the Black Sea area. James Rives Childs, of the American Expeditionary Forces,
printed the intercept log in Appendix B of *General Solution of the ADFGVX Cipher System*: 688 entries. A
public transcription of that log (creilly11235/adfgvx-1918, October 2026) marks 83 entries
unsolved.

This repository is the reproducible record of one attempt to find out which of those 83 are
still open, and whether the known daily keys read any of them. In short:

- **Of 49 log entries listed as unsolved, 22 read under the known daily key of their period with
  at most two symbol insertions or deletions.** Each reading was reproduced by a second,
  independent implementation, and an adversary with the same freedom could not beat it. Each
  scores above a per-message null of 2,940 draws. The family-wise false-detection bound for this
  test is 49/1471, about 3.3%, supported by a mask-matched null rather than proved. There is
  **no** valid bound for the joint attacks (J2/J3) on damaged groups, and so none for strand J as
  a whole.
- **"Read" means the key is identified and the decryption reproduced, not that the text is
  legible.** Up to 40% of the letters in a reading are lost (p071A2), and the unknown share of
  each is given.
- **Seven of the 22 had already been read or summarised publicly.** For the other 15 no public
  reading was found. That is **not** a claim of a first solution: Lasry et al. (2017) read 618 of
  668 messages under the same keys and published no per-entry list, so these may well have
  been read already. "No public reading" is as of our run on 2026-11-01: a public edition,
  [icekylinx/adfgvx-cipher](https://github.com/icekylinx/adfgvx-cipher), created on 2026-11-02, has
  since published readings of many of these units.
- A 23rd detection (p218A) was beaten by a wrong key with many blank cells, so it stays a
  detection and is not counted as a reading.
- Four outside claims about Klaus Schmeh's 2017 list of open messages were tested by replication
  (strand R). One is PARTIAL (the decryption reproduces;
  its significance was not established either way), three are REPRODUCED in a stated, limited sense.
- Joint attacks on groups of messages with an unknown transposition found nothing that reads.
- The known-key test caught only 5 of 12 positive controls, so its 26 negatives exclude nothing.

The full story, with the method, the wrong turns and what each check caught, is the notebook
entry: **https://labs.compacto.land/results/adfgvx-1918/**

`findings/adfgvx-1918.md` is the authority. Where anything here or in the entry disagrees with
it, it wins.

## What is in each folder

| path | what |
|---|---|
| `findings/adfgvx-1918.md` | The finding: both strands, the per-unit table, what would make it wrong, what was not established |
| `findings/adfgvx-1918-prereg.md` | The pre-registration, frozen before any unread text was decrypted, with its revisions, clarifications and one disclosed amendment |
| `ciphertexts/` | creilly's verbatim copy of Childs's log (`adfgvx-1918-log.records.json`) and of the 22 published keys (`adfgvx-1918-log.keys.json`); Schmeh's 2017 list (`adfgvx-1918-open.txt`); our blind transcription of the scan (`adfgvx-1918-scan-blind.json`), the adjudicated reading used as the primary text (`adfgvx-1918-scan-transcription.json` and `.md`), the readers' raw output (`adfgvx-1918-scan-raw/`) and the tools (`adfgvx-1918-scan-tools/`). `ciphertexts/README.md` gives every file's source, access date and sha256 |
| `search/adfgvx/` | The computation team's code: corpus, mutilation census, duplicate screen, the trigram scorer (`lm.py`), the C attack (`jattack.c`) and the strand J driver (`strandj.py`) |
| `results/` | Every output: J0 (pool, controls, groups), the J1/J2/J3 null draws and runs, the robustness re-run on creilly's transcription, the duplicate screens, the census, the power tests, and the trials log |
| `verify/adfgvx/` | The second implementations, written without access to `search/`: strand R and the census (`REPORT.md`), the J1 reproduction (`J1-repro.py`, `J1-REPRO.md`), the J3 reproduction (`J3-repro.py`, `J3-REPRO.md`) |
| `referee/` | The referee's report, Parts A to K (`adfgvx.md`), and its own re-runs (`adfgvx-r/`); `j1mask.py` and `j1mask.jsonl.gz` are the Part K mask-matched null |
| `adversary/` | The adversary's reports (`adfgvx*.md`) and code (`adfgvx/`): the free-key baseline, wrong keys at equal freedom (`j1/wrongkeys.py`), random keys, edit caps, the J3 mask bias (`j3/`) and its own J1 mask-matched null |
| `literature/` | Prior work (`adfgvx.md`), the per-unit novelty check (`adfgvx-strandj-novelty.md`), and copies of the outside transcriptions |

## The source images

The primary source is a free scan of Childs, *General Solution of the ADFGVX Cipher System*
(Aegean Park Press), linked from Richard Bean's index at
https://richardbean.id.au/misc/kryptos/aegean-park-press.html (Google Drive file
`1_JiNMck7eUvdrOTrH7fsj1Yh44t-VSC6`, 248 pages, sha256
`157e41a12374c6c1f464f52f587fbf6be6e0e08706ac35f7f4b0d66dc798ad06`). It is not included here.
PDF page = Childs page + 3 for every entry (fields `childs_page` and `pdf_page` in
`ciphertexts/adfgvx-1918-log.records.json`).

## How to run the checks

You need a C compiler and Python 3.10 or later; nothing else is installed and nothing is
downloaded. From the repository root:

```sh
cc -O2 -o e2 adversary/adfgvx/j1/e2.c -lm
mkdir -p tmp
python3 -I search/adfgvx/lm.py lm.tab
```

Then the six checks the export runs from a fresh copy before it creates this repository
(summarised below; they take
about three minutes in all):

1. **Inputs.** The scan transcription, keys, log, Schmeh's list, blind pass, mapping overrides
   and the rebuilt scorer table have the sha256 values the run recorded:
   `printf "%s  %s\n" <hash> <file> ... | sha256sum -c -`.
2. **Second implementation (gate i).** `python3 -I verify/adfgvx/J1-repro.py` decrypts all 23
   detections from text, key and edit list alone with its own code, and must print
   `reproduced 23 / 23`; its regenerated `J1-REPRO.md` is byte-identical to the committed one.
3. **The search, independently.** `J1SRC=. J1LM=lm.tab J1E2=./e2 python3 adversary/adfgvx/j1/repro.py`
   redoes the at-most-two-edit search for all 49 targets with the adversary's own C code and
   must end `mismatches: 0 of 64`.
4. **Wrong keys at equal freedom (gate ii).** `J1SRC=. J1LM=lm.tab J1E2=./e2 python3 adversary/adfgvx/j1/wrongkeys.py`
   scores every detection under each of the other 21 keys; `results/wrongkeys.tsv` must equal
   `adversary/adfgvx/j1/results/wrongkeys.tsv`.
5. **The mask-matched null.** `TMPDIR="$PWD/tmp" python3 -I referee/adfgvx-r/j1mask.py . 100 j1mask-100.jsonl`
   re-runs the first 100 of the referee's 1,470 seeded draws per detection with the computation
   team's own attack (use 1470 for all of it, about 30 minutes).
6. **The table.** A short script (the last `verify` command in the manifest) recomputes every
   column of the per-unit table in `findings/adfgvx-1918.md` from the files above, checks that
   all 1,470 mask-matched draws per detection score below S and that step 5's draws equal the
   committed ones, and prints the J1 bound.

The longer runs (the J1 nulls, about 75 minutes each half; the adversary's 59,800 random keys;
the J2/J3 nulls) are not part of the quick check. Their commands are in
`results/adfgvx-J.md`, `adversary/adfgvx-j1.md` and `adversary/adfgvx-j3.md`, and their outputs
are committed here.

## Credits

The keys are Lasry, Niebel, Kopal and Wacker's (Cryptologia 41(2), 2017), as published in
creilly11235/adfgvx-1918 @ `e60da03`, which also transcribed the whole log. Earlier public
readings of four of these entries are credited per unit in `literature/adfgvx-strandj-novelty.md`:
Norbert and Max Baertl in the comments on Klaus Schmeh's blog (March 2017), and AyushAg1002 on
dbourdeau/cyphersolver issue #181 (October 2026). 0wwafa/adfgvx-1918 issue #1 summarised three
more. The work here was done by a team of AI chats (a lead, a computation team, independent
second implementations, a transcriber, a referee, an adversary and literature scouts) between
31 October and 1 November 2026.
