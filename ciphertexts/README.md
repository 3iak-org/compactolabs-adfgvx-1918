# Ciphertexts

Every transcription a finding relies on. Each file keeps the header its literature scout gave it
(source, URL or page, access date). Copied from `literature/*-transcriptions/` by `dev` on
2026-10-31 for the Phase 0 triage. The exception is the ADFGVX 1918 log: `adfgvx-1918-scan-*` is our
independent blind transcription of the Childs scan (transcribe-adfgvx, 2026-10-31/11-01).

Checksums are SHA-256. **file** is the file as committed. **body** is every non-`#` line with all
whitespace removed, which is the ciphertext itself for the single-text files and survives
re-wrapping.

| file | what | n | body sha256 | file sha256 | status |
|---|---|---|---|---|---|
| `dagapeyeff-1939.txt` | d'Agapeyeff, *Codes and Ciphers* (1939) challenge, via Wikipedia | 395 digits (392 + `000` pad) | `8aa2e4296817f2ab9e8d9f2a79534dd3ab4c169022749fbffe13d9947dd1cb14` | `d9a6be908b0172d82fd95cdda73eb27e0fb9b0a55915a518bc13177652c88aaf` | 8 sources digit-identical (`literature/dagapeyeff.md` §2). No primary scan compared: the IA 1974 facsimile is borrow-only. |
| `dct-reloaded-1.txt` | MysteryTwister "Double Column Transposition Reloaded" Part 1, official file | 613 | `67af3648274c1ac092a027495238c50455dd61cc3d93ba6d99ff338f74ff263a` | `d1e59432850f73545ea2ac68e0c2f9c0648393c41f0f15d5111ddb16d2f6374d` | Body hash equals the hash of the file as downloaded from mysterytwister.org. |
| `dct-reloaded-2.txt` | same, Part 2 | 637 | `2d8567e7f8aa60a66e47258a45f8d89831922a447bd8f9c8e9b3c472a0bcf4b3` | `4b065c9de65de21334868d66a8e80ec125d55645790d4b686abfc3ef27099d9a` | Official file; matches the PDF by eye only. |
| `dct-reloaded-3.txt` | same, Part 3 | 1006 | `424f4232f81bcbdb6425b506c7e475d328e66407cc170e406b75b4d6a9d5f32b` | `12db5fd3baf1f3ec0bb6d9d9ab8d14de1f14bbf581f4b02d9169e11bab3475a2` | Official file; identical to Schmeh's 2018 blog printing. |
| `kryptos-k4.txt` | Kryptos K4, via Wikipedia | 97 | `eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab` | `811771c167a718dab11d3528b113b9fe6c8631469b8cde37b9ba29f71ccff109` | Five copies agree; none independent of the community copy (`literature/kryptos-k4.md`). |
| `orpo-doppelkasten-1942-UNVERIFIED.txt` | Ordnungspolizei double-box radiograms, 27 Feb 1942, Bourdeau's transcription of Weierud 2020 | 968 letters + 2 illegible (body hash includes message labels) | `d9737447a8cb113c49a1de065750ed125b66855e443045c6e57416070f7f5898` | `ff12c4f761133d29ff02e8e71405715a000e638f91d36cda61a65685cbf816b5` | **Not compared with Weierud's PDF images.** Do not rely on it until that is done. |
| `adfgvx-1918-open.txt` | WWI ADFGVX messages still open (Childs transcript, Lasry's list on Schmeh's page) | 22 messages (body hash includes prose and labels) | `1a88c1a09af18ac2fce814dceaa5e5ea419b57d786082a8b93f0be90e7a4f725` | `9362c3d28ee220d21118296446d8d9337a6d02734162844657de1dd62e21df94` | Agrees with Bourdeau's copy on all 22. Which ones are still open: see the header. |

## ADFGVX 1918 (lead-adfgvx)

One row per file. Each row gives the source, the access date and the sha256. A derived file
names the script that makes it; its sha256 changes with every run because of the provenance
header, so the stable checksum is that of its source.

| file | what | source | accessed | sha256 |
|---|---|---|---|---|
| `adfgvx-1918-open.txt` | Schmeh's 2017 list of 22 unsolved ADFGVX messages, "Provided by George Lasry" (lead-adfgvx's copy, from triage) | https://scienceblogs.de/klausis-krypto-kolumne/unsolved-adfxvx-messages-from-world-war-i/ | 2026-10-31 | `9362c3d28ee220d21118296446d8d9337a6d02734162844657de1dd62e21df94` |
| `adfgvx-1918-log.records.json` | Verbatim copy of `data/records.json`. All 688 entries of Childs's Appendix B intercept log: id, Childs page, PDF page, page date, heading (OCR, verbatim), part, header symbol count, log symbols as printed, status, key id, plaintext, method, notes | github.com/creilly11235/adfgvx-1918 @ `e60da03db4ea673c70c8c3286a4dc4d37176909c` (2026-10-26) | 2026-10-31 | `4a27e2e163ef73ca5c20f3c6cb67942258eaed25a77c966bd96616a549c37c40` |
| `adfgvx-1918-log.keys.json` | Verbatim copy of `data/keys.json`: 22 keys (Lasry et al. 2017's 14 period keys, 5 from Childs, 1 from Childs's 1919 history, 1 from 2017 blog comments, 1 of creilly's own). Square: 36 cells, rows/columns ADFGVX, `?` = blank in the source | same commit | 2026-10-31 | `095de9ce1e9ec903db6bf9588b4fa8932272d7fc49ab6f9d5925d5008116f2a7` |
| `adfgvx-1918-log.messages.json` | Verbatim copy of `data/messages.json`: creilly's two new readings (Childs p.176 "2305", p.153), with filled squares and gap positions | same commit | 2026-10-31 | `beed069aaf8a302f3da4c4abdef7ca9e8da61faedff990f5225ccddb42c674f1` |
| `adfgvx-1918-log.tsv` | Derived: one row per entry with the header fields, status and symbols, plus counts of slots, letters and lost marks | `search/adfgvx/build_corpus.py` from records.json | 2026-10-31 | (derived) |
| `adfgvx-1918-log.keys.tsv` | Derived: one row per key with period, width, source, blank-cell count, `in_lasry_2017` and `in_16`. The "16 known keys" of 0wwafa PAPER §5.3 are Lasry's 14 + CHI (`chi_2017_comments`) + TRUPPENVERSCHIEBUNG (`dec09_history`, the key that reads Childs p.217) | `search/adfgvx/build_corpus.py` from keys.json | 2026-10-31 | (derived) |
| `adfgvx-1918-log.plaintexts.tsv` | Derived: the 595 entries with a plaintext. These are creilly's own 2026 decryptions. Lasry et al. 2017 published the keys and totals (618 of 668 cryptograms), not a plaintext per entry | `search/adfgvx/build_corpus.py` from records.json | 2026-10-31 | (derived) |
| `adfgvx-1918-scan-worklist.json` | The 83 Unsolved ids and 30 calibration ids (fixed rule, stated in the file's script) for the scan transcription; ids, pages and headers only | `adfgvx-1918-scan-tools/select_entries.py` from records.json | 2026-10-31 | (derived) `9cd9498f105945295b80d0ebd014530231c6e66cac26a0b8cf4bd92bf46a9505` |
| `adfgvx-1918-scan-blind.json` | Blind transcription of every cipher block (362 blocks, 70,662 symbols) on the 80 PDF pages holding a target, read before any creilly symbol was seen; first committed at `95ceb08` | Childs, *General Solution of the ADFGVX Cipher System* (Aegean Park Press) free scan, Google Drive `1_JiNMck7eUvdrOTrH7fsj1Yh44t-VSC6` via richardbean.id.au/misc/kryptos/aegean-park-press.html; PDF sha256 `157e41a12374c6c1f464f52f587fbf6be6e0e08706ac35f7f4b0d66dc798ad06`; built by `adfgvx-1918-scan-tools/build_blind.py` | 2026-10-31 | (derived) `7cd5a1381f92b98fdf0aeba181510306fbfb7919c3ef242fe539d511ac034e47` |
| `adfgvx-1918-scan-transcription.json` / `.md` | Our reading of the 83 Unsolved + 30 calibration ids, mapped to page spans; calibration error rate; blind agreement with creilly and the adjudication of every disagreement | the scan above + records.json; `adfgvx-1918-scan-tools/build_final.py` | 2026-11-01 | (derived) |
| `adfgvx-1918-scan-mapping-overrides.json` | The two hand overrides of the id-to-span mapping (p153B, p220C), each with its reason | hand, after the image check | 2026-11-01 | `fd1845b461c1ab9f5f6ea88f0e00f362961f73845b0026ce10e2541a8f15a72b` |
| `adfgvx-1918-scan-raw/` | Reader outputs (readers1, readers2, with their protocol), cross-check outputs, adjudications and their verdicts | as above | 2026-10-31 to 11-01 | (derived) |
| `adfgvx-1918-scan-tools/` | Scripts for all of the above (crop, OCR + templates, comparisons, mapping, calibration) | written here | 2026-10-31 | — |

## Notes on the ADFGVX transcriptions

- **Two transcriptions overlap: Schmeh's 22 and creilly's log.** Every disagreement is listed
  in `results/adfgvx-transcription-diff.md`.
  - 11 of the 22 entries agree exactly. The other 11 differ, mostly in lost-group marks.
  - Page 164 (both parts) and Page 158 differ most. creilly marks p.158 (`p161D`) as a
    "Duplicate entry", a log row joining the symbols of two others.
- **`printed` is creilly's log transcription, not the page.** For 44 solved entries creilly
  re-read the page, and the re-reading differs from `printed` by a median of 7 edits
  (`results/adfgvx-mutilation.tables.md` §9). No unsolved entry has been re-read.
- **The page images** are in the Aegean Park Press PDF, through Richard Bean's index
  (https://richardbean.id.au/misc/kryptos/aegean-park-press.html). creilly's page file for each
  entry gives its PDF page. Our independent transcription of the 80 target pages is
  `adfgvx-1918-scan-blind.json` / `adfgvx-1918-scan-transcription.*`.

## Checks (2026-11-01)

- **The lit-adfgvx copy matches ours.** `literature/adfgvx-transcriptions/creilly-childs-log-688.json`
  on `agent/lit-adfgvx` (sha256 `e5ff5899...40b3`) is a field subset of our
  `adfgvx-1918-log.records.json` (`4a27e2e1...7c40`). It has the same 688 ids in the same order,
  and is identical on all 13 fields it keeps (id, childs_page, pdf_page, date, header, part,
  count_in_log, symbols_in_log, printed, key, credit, note, status). It omits plaintext,
  ciphertext, method, confidence, unread_symbols, key_by, published_by and text_marks.
- **The key list is 22, not 16** (lit-adfgvx §2.3). Every key comes from creilly `keys.json`, and
  its `source` column says where creilly took it:

  | source | keys |
  |---|---|
  | `lasry` | 14 |
  | `childs` (Jul 18, Jul 22, Aug 3, Aug 8, Aug 20) | 5 |
  | `childs_history` | 1 |
  | `repair key list` (the CHI key) | 1 |
  | creilly's own (p.153) | 1 |

  We use creilly's values throughout. lit-adfgvx notes discrepancies against Childs's own tables
  (e.g. Childs's Nov 4-6 transposition lacks an element). We have not re-derived any key from
  Childs.
- **The net indicator line** (RICHI-n, CHI-n, RIZI-n) under each heading is NOT in creilly's
  `header` field. Per-entry values known from other sources are in `results/adfgvx-clusters.md`
  §7b.
