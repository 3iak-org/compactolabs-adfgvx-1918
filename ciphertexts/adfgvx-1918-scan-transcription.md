# ADFGVX 1918 log: an independent reading of the 83 unread entries from the scan

transcribe-adfgvx, 2026-10-31 to 2026-11-01. Blind pass committed at
`95ceb080f9d5ccdffa9adc127650db03d934a599` (`ciphertexts/adfgvx-1918-scan-blind.json`) before any
creilly symbol was read.
- That commit is kept reachable by the tag `transcribe-adfgvx-blind-pass`.
- After a rebase onto lead-adfgvx, the same content is commit `1e3a3a4` on the branch. The
  files under `ciphertexts/adfgvx-1918-scan-*` are identical in the two. Final file: `ciphertexts/adfgvx-1918-scan-transcription.json`.

**Ladder.** One reading team and one adjudicator (me) produced this. It is a single transcription,
so nothing below is [C]. The counts are exact counts *of this reading*. The error rates are [S]:
calibrated on a stated sample of 30 entries. Extrapolations to the unread entries are [H].

## Answer

1. **Calibration error rate (headline), [S] 2026-11-01:** **1 symbol wrong in 6,146** truth-fixed
   symbols, i.e. 0.016%. The 95% upper bound is 0.077% (exact Poisson, 1 event). The sample is 30
   solved entries chosen by a fixed rule before any was viewed. The one error is a substitution:
   an E/F overstrike read as E where the truth is F (p195A.2). There were 0 insertions and 0
   deletions. Two more differences from the truth are features of the page, not reading errors
   (see Calibration).
2. **Blind agreement with creilly, before adjudication, [exact count] 2026-11-01:**
   - 83 Unsolved ids: **13,617 of 14,325 aligned columns equal (95.06%)**. Where both
     transcriptions have a symbol in the column, **13,617 of 13,692 agree (99.45%)**.
   - 30 calibration ids: 6,261 of 6,266 equal (99.92%).
3. **After adjudication, [exact count, single adjudicator] 2026-11-01:** every one of the 713
   differing columns (708 Unsolved + 5 calibration) was re-viewed on the image. No column turned
   out to be one where creilly is right and the blind pass wrong.
   - 7 Unsolved columns are genuinely ambiguous (overstrikes and blots). The calibration
     overstrike is an 8th.
   - So the final reading is the blind reading unchanged, and the final agreement figure equals
     the blind one. What adjudication changes is the classification of the 708 Unsolved columns:

| category (Unsolved) | columns | what it is |
|---|---:|---|
| creilly omits printed symbols | 589 | whole lines, groups, final short lines and trailing runs of printed lost-group dashes missing from creilly's row |
| page prints a letter outside ADFGVX | 37 | U, T, N, R, S, E, W, O, B, C, K, I as printed; creilly writes a lost mark or the nearest letter |
| creilly adds or pads | 26 | lost marks added around parenthesised symbols `F(X)DFA`, after 4-letter groups, at line breaks, for dots and hand strokes; one trailer appended |
| gap placeholder | 25 | the page prints "(INTERFERENCE)" or "(and several groups Missing)". creilly writes 10 or 15 lost marks; we write none, because the page does not print the gap's length |
| creilly misreads a clear glyph | 17 | e.g. p153B4 `FXVGV XXFAX AVXVV` read with A for X three times |
| ambiguous glyph | 7 | overstrike or blot; both readings recorded |
| not on the page | 6 | p220C's whole row, `VD-A-D` |
| equivalent | 1 | `?` (ours) vs `-` (theirs) for the same unreadable mark |

**What would have to be true for this to be wrong.**
- (a) The readers and I share a systematic misreading that the OCR also makes. The OCR is
  template matching on the same images, so a glyph that looks like the wrong letter fools both.
  The calibration cannot see such an error either, if creilly made it too. See "circularity"
  below.
- (b) The calibration entries are easier than the unread ones. They are: they are entries
  whose transcription decrypts as it stands, so the error rate on the hard Unsolved pages can be
  higher.
- (c) My adjudication favoured our reading. Every verdict and its reason is in
  `ciphertexts/adfgvx-1918-scan-raw/creilly-adjudication/` with the montage coordinates, so a
  second adjudicator can re-check them.

## Source

- The scan is Childs, *General Solution of the ADFGVX Cipher System* (Aegean Park Press). I took
  the free PDF from Richard Bean's index (richardbean.id.au/misc/kryptos/aegean-park-press.html):
  Google Drive file `1_JiNMck7eUvdrOTrH7fsj1Yh44t-VSC6`, 248 pages, downloaded 2026-10-31.
  - sha256 `157e41a12374c6c1f464f52f587fbf6be6e0e08706ac35f7f4b0d66dc798ad06`. That is the full
    sha, and it matches the brief's 157e41a1…798ad06.
  - Each page is a 2409×3437 JPEG, i.e. 300 dpi. PDF page = Childs page + 3, as the brief says.
- creilly's ids and the "Unsolved" list come from `adfgvx-1918-log.records.json`, reading only
  `id, childs_page, pdf_page, date, header, part, status, method` before the blind commit
  (`select_entries.py`).

## Method

1. **Work list** (`adfgvx-1918-scan-worklist.json`, committed 7cb7476 before any page was
   viewed): the 83 Unsolved ids and 30 calibration ids.
   - Calibration rule: `status == "Solved"` and `method == "period key, as transcribed"`
     (465 candidates). Sort by (pdf_page, id) and take every ⌊i·465/30⌋-th.
   - creilly's ids map onto page blocks in no fixed pattern (`p072B3` is the page's "2 TL";
     `.2` and `_` suffixes). So I transcribed **every cipher block on the 80 pages** that hold
     a target: 362 blocks, 70,662 symbols. The ids were mapped afterwards.
2. **Reader 1, every page, blind.** Eight reader agents followed one written protocol
   (`scan-raw/readers1/PROTOCOL.md`): strips of at most 6 lines at native resolution, zoom on
   doubt, transcribe as printed, `-` for a printed dash, `?` for unreadable, uncertainties
   listed.
3. **OCR channel, every page.** This is a template OCR written here
   (`adfgvx-1918-scan-tools/ocr*.py`, templates `ocr_templates.npz`). It shares no code and no
   method with the readers.
   - How it works: page scale normalisation, line and word segmentation on the typewriter's
     pitch, then normalised correlation against six letter templates. The templates were seeded
     from 4 lines of p.72 read by eye, then self-trained, with per-page adaptation.
   - Compared group by group with reader 1 (`compare_groups.py`): **55,146 symbols paired;
     53,684 agree, 1,428 OCR abstentions, 34 conflicts** in 43 contested groups.
   - Every contested group was adjudicated on the image (`scan-raw/adjudication/`). The OCR
     caught **5 reader errors**, all clear on the image: 4 letter-order slips (`VXGVV` for
     `VXVGV` and the like) and 1 letter. The other contested groups were letters the OCR has no
     template for (U, E, K, …), or ambiguous overstrikes.
4. **Reader 2, on the 24 pages the OCR reads worst.** Three more reader agents worked
   independently, blind to reader 1 (`scan-raw/readers2/`). **26,262 of 26,269 paired symbols
   agree with reader 1.** The 7 differences were adjudicated on the image:
   - 1 was a reader-1 error (p167 `VGVJV` → `VGVVV`: a V whose left stroke did not print);
   - 1 was a reader-2 error;
   - the rest are overstrikes.
5. **Blind commit** `95ceb08` (tag `transcribe-adfgvx-blind-pass`; `1e3a3a4` after rebase), with all of the above. 17 adjudications are recorded; 6 of them
   change reader 1's reading.
6. **Only then** did I read creilly's symbols.
   - **Mapping** (`map_spans.py`): each record was aligned against the blocks of its page and
     its neighbours. A record may match part of a block (semi-global alignment) or two blocks
     joined.
   - The mapping is one-to-one apart from the splits and joins listed below. Two overrides,
     each with its reason, are in `adfgvx-1918-scan-mapping-overrides.json`.
   - **Diff** (`final_diff.py`): minimal edit alignment of our span against creilly's
     `printed`. When a record is the only one on its block, the span is widened to the whole
     block, so a printed run creilly omits shows as a difference instead of being aligned away.
   - **Adjudication**: 136 items, one per run of differences within a printed line. Each was
     viewed as a full-line crop (`adj_items.py`, `adj_show.py`, `montage.py`) and zoomed
     where needed. The verdicts are in `scan-raw/creilly-adjudication/`.

**One bug, found and fixed after the blind commit.**
- `build_blind.py` treated any token with a parenthesis *inside* it, such as `F(X)DFA`, as an
  annotation, so it left those letters out of the derived `symbols` field.
- The `lines`, which are the reading, were unaffected. The fix changed the symbol counts of
  4 blocks (p72 b0, b1, b2; p110 b4), and all four now match their header counts.
- The blind file was regenerated from the same committed reader and adjudication data. Its
  `lines` are byte-identical to `95ceb08`'s.

## Calibration

- Truth is creilly's plaintext re-encrypted under its key with comp-adfgvx's `engine.encrypt`
  (`calib_truth.py`). `*` marks a position the plaintext does not fix: 120 of 6,266.
- Our blind symbols, aligned to the truth with `*` as a wildcard (`calib_score.py`, output
  `scan-raw/crosscheck/calibration_score.json`):
  - 6,143 of 6,146 equal;
  - 2 substitutions;
  - 0 symbols we have that the truth lacks;
  - 1 symbol the truth has that we lack.
- Each difference, checked on the image:

| id | ours | truth | verdict |
|---|---|---|---|
| p153B5 | `-` | F | the page prints a dash with an asterisk above it (`F*GFX`): a printed lost mark, not a misreading |
| p163D1 | (none) | D | the page prints 140 symbols, matching the header RICHI-140; the message lost a symbol before it reached the page |
| p195A.2 | E | F | **our error**: E typed over F (or the reverse), read as E. Counted as the 1 error |

**Circularity, which limits what the calibration can see.**
- These entries are "as transcribed": creilly's log transcription decrypts under the key as it
  stands.
- Re-encrypting the plaintext therefore reproduces creilly's reading at every position where
  the plaintext is a raw decrypt. A substitution in the transcription survives the round trip as
  a wrong plaintext letter.
- So the calibration measures our agreement with a reading that is known to decrypt. It cannot
  see an error that we and creilly share.
- I found 1 position where our reading and creilly's differ (p163D1 `VVGXG`, creilly `VVGAG`).
  The truth has `*` there; the image reads X.

**Extrapolation [H].** At the calibration rate, the 14,266 symbols of the Unsolved spans would
hold about 2 residual errors (upper bound about 11). The Unsolved pages include the worst of the
book: single spacing, overlapping lines, a second typewriter on pp.139–141, heavy overstrikes.
Treat that figure as a floor, not an estimate.

**Coverage of the Unsolved spans by the two cross-checks** (by line, [exact count]): 14,266
symbols in 79 blocks.
- 11,118 lie on lines the OCR matched. The OCR abstains on some symbols within those lines.
- 5,031 lie on lines reader 2 matched.
- **238 (1.7%) have neither cross-check.** Most are short last lines and dash rows.

## What the scan shows that the records lack or garble

- **Splits.** One page block is split into two records: its first printed line is one record,
  the rest another.
  - p083B2 = p.83 "2 TL RICHI-248" [0:40], and p083B = [40:248].
  - Likewise p101B2 / p101B and p142A2 / p142A.
  - Together the two records of each pair cover the block exactly.
- **Join.** p0924 is two page blocks run together: "2 TL RICHI-290" (290 symbols) and "3 TL
  RICHI-358" (258 printed, with "(missed 20 groups)"). It is a 548-symbol row, and its alignment
  has 0 edits. This is the same kind of fault comp found in p149C1.
- **p153B4 / p153B** are one block, "4 TL" on p.153.
  - Its printed lines 2 and 3 are typed half a line apart and overlap. creilly's p153B merges
    them into one line, which loses about 50 symbols and garbles the rest.
  - Both of our readers read the two lines identically. Our p153B is lines 2–5, [80:202].
- **p220C is not ciphertext.** Heading C) on p.220 has one block, RICHI-170, which is p220C.2
  (Solved). Nothing on the page matches the 6-symbol row `VD-A-D`; it looks like letters from
  the plain-text preamble or trailer.
- **Wrong heading.** creilly gives p141B.2 the heading "B) LP v NKJ 00.15 November 5th". On
  the page, RICHI-286 sits under **"C) UKS RAT v NKJ (10.32 p.m. November 6th, 1918)"**, below
  a second date line, "6th November 1918".
- **Garbled headings, corrected from the page:**
  - p1154 is "C) OUI v OSM (5.59 p.m., November 4th)"; creilly has "(4) 1700";
  - p072A is "NKJ v ---" (creilly "OKI w-");
  - p076A is "POT v NKJ" (creilly "Et v NKJ");
  - p173A is "--- v ---";
  - p192A is "CZ v CM … November 13th" (creilly "CZ v OM … 12th").
- **Heading date differs from the page's date line** in 36 of the Unsolved ids. Most are one
  day apart, which is an overnight message. The larger gaps:
  - p076A: heading 8 November on a page dated 26 October (+13 days);
  - p072A and p072B1: +6;
  - p074A.2, p087C, p139A2, p197D1 and p207_2: +2;
  - p110D, p140A5, p140A6, p140B and p192A: −1.
  - Caveat: "page date" is the page's top date line, and some pages carry a second one
    mid-page (pp.141, 161, 177).
- **Call-sign nets** (the block label):
  - 65 Unsolved ids are RICHI;
  - **12 are RIZI**: p102A, p104D2, p112D, p123C, p130B2, p140B, p185A, p185C, p186D, p192A,
    p200C, p201E;
  - **2 print "CHI-" with no "RI"**: p071A1 "CHI-220", p201D "CHI-170";
  - p148A has no label (a dash run);
  - p215A.3 is labelled "4 TL (Missed start)".
- **Symbol count vs the printed header.** The header number is in the JSON (`header_count`)
  next to our count. They differ for 35 of the 79 blocks under the Unsolved ids. Small
  differences come from 4- or 6-letter groups; large ones from printed "(jammed)",
  "(interference)" or "missing" gaps.
  - The large shortfalls (printed of header):
    - p074A.2: 85 of 192, "(interference)";
    - p087C: 118 of 244, "(Balance jammed)";
    - p0924's 3 TL: 258 of 358, "(missed 20 groups)";
    - p119A1: 160 of 222, "(Balance jammed)";
    - p157A2: 118 of 162;
    - p177A3: 79 of 98, "(Did not finish)";
    - p190B: 140 of 214, "(Jammed …)";
    - p197D1: 45 of 214;
    - p207_2: 242 of 282;
    - p215A2: 160 of 284;
    - p218B1: 145 of 220, "(and several groups Missing)";
    - p222C: 284 of 394, "(jammed)".
  - Some blocks print more symbols than the header says:
    - p192A: 90 under "RIZI-46";
    - p186D: 37 under "RIZI-27";
    - p174A3: 261 under 252, including a struck-through group and handwritten groups.
- **Notation creilly does not keep:**
  - parenthesised symbols `F(X)DFA`, `FDX(X)-X(X)VGX`, `XGA(X)D`, a lone `(X)`;
  - a single typed W in one cell (p071A1 `AVWX-`), which creilly reads as VV. With W as one
    symbol the block has exactly 220 = header;
  - 4-letter groups, which creilly pads with a lost mark.
  - What Childs meant by the parentheses is not established here.
- **Letters outside ADFGVX** are printed in 12 of the Unsolved ids: B, C, E, I, K, N, O, R, S,
  T, U, W. Among the other blocks on these pages there are also Z, L, Q, H. We keep them as
  printed; `non_adfgvx` per entry.
- **Duplicate and near-duplicate messages** (noticed by readers, not used to change any reading):
  - p186 RIZI-27 ≈ RIZI-36;
  - p104 D ≈ A;
  - p192 C = p200 B;
  - p200 E = p201 C;
  - p200 C ≈ p201 B;
  - p161 RICHI-100 ≈ p165 RICHI-100;
  - p147 2 TL ≈ p155 E) 2 TL;
  - p175 B RIZI-40 = p177 D.

## Per-entry table (Unsolved)

- **spans** is page.block[start:end] in our symbols.
- **equal/cols** is blind agreement with creilly.
- The category columns count the differing columns, by verdict.
- **OCR/R2 checked** counts the block symbols on lines each cross-check matched.

| id | page/block | label (net) | header | ours | creilly | equal/cols | omits | adds | non-ADFGVX | misread | ambig | other | OCR/R2 checked | notes |
| p062A | 62.0[0:225] | 1 TL RICHI-220 (RICHI) | 220 | 225 | 225 | 225/225 | 0 | 0 | 0 | 0 | 0 | 0 | 225/0 of 225 | hdr [22, 9] vs page [21, 9] |
| p071A1 | 71.0[0:220] | 1 TL CHI-220 (CHI) | 220 | 220 | 222 | 218/222 | 0 | 0 | 4 | 0 | 0 | 0 | 220/0 of 220 | letters KW |
| p071A2 | 71.1[0:186] | 2 TL CHI-186 RICHI-186 (RICHI) | 186 | 186 | 186 | 186/186 | 0 | 0 | 0 | 0 | 0 | 0 | 186/0 of 186 |  |
| p072A | 72.0[0:220] | RICHI-220 (RICHI) | 220 | 220 | 228 | 219/228 | 0 | 8 | 0 | 1 | 0 | 0 | 220/0 of 220 | hdr [11, 10] vs page [5, 10] |
| p072B1 | 72.1[0:329] | 1 TL RICHI-330 (RICHI) | 330 | 329 | 326 | 322/331 | 6 | 2 | 1 | 0 | 0 | 0 | 329/0 of 329 | hdr [11, 10] vs page [5, 10]; letters U |
| p073B | 73.2[0:206] | RICHI-206 1 TL (RICHI) | 206 | 206 | 206 | 206/206 | 0 | 0 | 0 | 0 | 0 | 0 | 176/0 of 206 |  |
| p074A.2 | 74.1[0:85] | 2 TL RICHI-192 (RICHI) | 192 | 85 | 80 | 80/85 | 5 | 0 | 0 | 0 | 0 | 0 | 80/0 of 85 | hdr [8, 10] vs page [6, 10] |
| p076A | 76.0[0:178] | RICHI-178 (RICHI) | 178 | 178 | 178 | 178/178 | 0 | 0 | 0 | 0 | 0 | 0 | 178/0 of 178 | hdr [8, 11] vs page [26, 10] |
| p083B2 | 83.2[0:40] | 2 TL RICHI-248 (RICHI) | 248 | 40 | 40 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 | 248/0 of 248 |  |
| p083B | 83.2[40:248] | 2 TL RICHI-248 (RICHI) | 248 | 208 | 209 | 208/209 | 0 | 1 | 0 | 0 | 0 | 0 | 248/0 of 248 |  |
| p087C | 87.2[0:118] | RICHI-244 (RICHI) | 244 | 118 | 120 | 118/120 | 0 | 1 | 0 | 0 | 1 | 0 | 118/0 of 118 | hdr [1, 11] vs page [30, 10] |
| p0924 | 92.0[0:290];92.1[0:258] | 2 TL RICHI-290+3 TL RICHI-358 (RICHI+RICHI) | 290+358 | 548 | 548 | 548/548 | 0 | 0 | 0 | 0 | 0 | 0 | 523/0 of 548 |  |
| p101B2 | 101.2[0:40] | 2 TL RICHI-266 (RICHI) | 266 | 40 | 40 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 | 266/0 of 266 | hdr [2, 11] vs page [1, 11] |
| p101B | 101.2[40:266] | 2 TL RICHI-266 (RICHI) | 266 | 226 | 226 | 226/226 | 0 | 0 | 0 | 0 | 0 | 0 | 266/0 of 266 | hdr [2, 11] vs page [1, 11] |
| p102A | 102.0[0:133] | RIZI-133 (RIZI) | 133 | 133 | 128 | 124/133 | 6 | 0 | 3 | 0 | 0 | 0 | 133/0 of 133 | hdr [2, 11] vs page [1, 11]; letters E |
| p102C | 102.2[0:136] | 1 TL RICHI-136 (RICHI) | 136 | 136 | 120 | 120/136 | 16 | 0 | 0 | 0 | 0 | 0 | 120/0 of 136 |  |
| p104D2 | 104.3[0:137] | 2 TL RIZI-137 (RIZI) | 137 | 137 | 137 | 135/137 | 0 | 0 | 1 | 0 | 0 | 1 | 137/0 of 137 | hdr [2, 11] vs page [1, 11]; letters S |
| p110D | 110.4[0:176] | RICHI-176 (RICHI) | 176 | 176 | 179 | 176/179 | 0 | 3 | 0 | 0 | 0 | 0 | 176/0 of 176 | hdr [1, 11] vs page [2, 11] |
| p112D | 112.5[0:258] | RIZI-258 (RIZI) | 258 | 258 | 258 | 258/258 | 0 | 0 | 0 | 0 | 0 | 0 | 258/0 of 258 |  |
| p114A | 114.0[0:202] | 1 TL RICHI-202 (RICHI) | 202 | 202 | 200 | 194/202 | 7 | 0 | 0 | 1 | 0 | 0 | 200/0 of 202 | hdr [4, 11] vs page [3, 11] |
| p1154 | 115.4[0:110] | RICHI-122 (RICHI) | 122 | 110 | 110 | 110/110 | 0 | 0 | 0 | 0 | 0 | 0 | 32/110 of 110 | hdr [4, 11] vs page [3, 11] |
| p119A1 | 119.3[0:160] | 13 TL RICHI-222 (RICHI) | 222 | 160 | 161 | 160/161 | 0 | 1 | 0 | 0 | 0 | 0 | 160/0 of 160 | hdr [4, 11] vs page [3, 11] |
| p123C | 123.2[0:56] | RIZI-56 (RIZI) | 56 | 56 | 56 | 56/56 | 0 | 0 | 0 | 0 | 0 | 0 | 16/56 of 56 | hdr [5, 11] vs page [4, 11] |
| p125B | 125.1[0:252] | RICHI-252 (RICHI) | 252 | 252 | 247 | 244/252 | 5 | 0 | 0 | 2 | 1 | 0 | 252/0 of 252 |  |
| p125D1 | 125.3[0:164] | 1 TL RICHI-164? (RICHI) | 164 | 164 | 160 | 160/164 | 4 | 0 | 0 | 0 | 0 | 0 | 160/0 of 164 |  |
| p130B2 | 130.2[0:152] | 2 TL RIZI-152 (RIZI) | 152 | 152 | 95 | 94/152 | 58 | 0 | 0 | 0 | 0 | 0 | 152/0 of 152 | hdr [5, 11] vs page [4, 11] |
| p139A2 | 139.1[0:92] | 2 TL RICHI-92 (RICHI) | 92 | 92 | 80 | 79/92 | 12 | 0 | 1 | 0 | 0 | 0 | 52/92 of 92 | hdr [7, 11] vs page [5, 11]; letters E |
| p140A5 | 140.1[0:215] | 5TL RICHI-252 (RICHI) | 252 | 215 | 215 | 205/220 | 5 | 0 | 0 | 0 | 0 | 10 | 0/215 of 215 | hdr [5, 11] vs page [6, 11] |
| p140A6 | 140.2[0:74] | 6TL RICHI (RICHI) | None | 74 | 69 | 69/74 | 5 | 0 | 0 | 0 | 0 | 0 | 49/74 of 74 | hdr [5, 11] vs page [6, 11] |
| p140B | 140.3[0:135] | RIZI-138 (RIZI) | 138 | 135 | 135 | 134/135 | 0 | 0 | 0 | 1 | 0 | 0 | 0/135 of 135 | hdr [5, 11] vs page [6, 11] |
| p141B.2 | 141.3[0:285] | RICHI-286 (RICHI) | 286 | 285 | 282 | 274/288 | 5 | 1 | 8 | 0 | 0 | 0 | 105/285 of 285 | letters COW |
| p142A2 | 142.1[0:40] | 2 TL RICHI-220 (RICHI) | 220 | 40 | 40 | 39/40 | 0 | 0 | 1 | 0 | 0 | 0 | 220/0 of 220 | letters B |
| p142A | 142.1[40:220] | 2 TL RICHI-220 (RICHI) | 220 | 180 | 180 | 180/180 | 0 | 0 | 0 | 0 | 0 | 0 | 220/0 of 220 |  |
| p148A | 148.0[0:192] | --------- (None) | None | 192 | 182 | 177/197 | 15 | 5 | 0 | 0 | 0 | 0 | 192/0 of 192 | hdr [7, 11] vs page [6, 11] |
| p153B4 | 153.4[0:80] | 4 TL RICHI----- (RICHI) | None | 80 | 80 | 77/80 | 0 | 0 | 0 | 3 | 0 | 0 | 80/202 of 202 | hdr [7, 11] vs page [6, 11] |
| p153B | 153.4[80:202] | 4 TL RICHI----- (RICHI) | None | 122 | 72 | 65/122 | 57 | 0 | 0 | 0 | 0 | 0 | 80/202 of 202 | hdr [7, 11] vs page [6, 11] |
| p155E | 155.4[0:104] | 1 TL RICHI---- (RICHI) | None | 104 | 104 | 104/104 | 0 | 0 | 0 | 0 | 0 | 0 | 104/0 of 104 |  |
| p157A2 | 157.0[0:118] | 2 TL RICHI - 162 (RICHI) | 162 | 118 | 118 | 117/118 | 0 | 0 | 0 | 0 | 1 | 0 | 118/0 of 118 |  |
| p160A | 160.0[0:83] | 1 TL RICHI---- (RICHI) | None | 83 | 84 | 83/84 | 0 | 1 | 0 | 0 | 0 | 0 | 83/0 of 83 | hdr [8, 11] vs page [7, 11] |
| p161E | 161.5[0:235] | 1 TL RICHI-236 (RICHI) | 236 | 235 | 235 | 235/235 | 0 | 0 | 0 | 0 | 0 | 0 | 0/235 of 235 | hdr [8, 11] vs page [7, 11] |
| p162B | 162.1[0:280] | RICHI-280 (RICHI) | 280 | 280 | 280 | 279/280 | 0 | 0 | 1 | 0 | 0 | 0 | 280/0 of 280 | letters R |
| p165A1 | 165.0[0:264] | 1 TL RICHI-268 (RICHI) | 268 | 264 | 264 | 264/264 | 0 | 0 | 0 | 0 | 0 | 0 | 63/264 of 264 | hdr [9, 11] vs page [8, 11] |
| p165C1 | 165.2[0:117] | RICHI--? 1 TL (RICHI) | None | 117 | 117 | 117/117 | 0 | 0 | 0 | 0 | 0 | 0 | 77/117 of 117 | hdr [9, 11] vs page [8, 11] |
| p166A | 166.2[0:234] | 15 TL RICHI-234 (RICHI) | 234 | 234 | 160 | 160/234 | 74 | 0 | 0 | 0 | 0 | 0 | 160/0 of 234 |  |
| p166A.2 | 166.3[0:121] | ----- RICHI---- (RICHI) | None | 121 | 121 | 121/121 | 0 | 0 | 0 | 0 | 0 | 0 | 121/0 of 121 |  |
| p167A | 167.0[0:240] | 3 TL RICHI-242 (RICHI) | 242 | 240 | 187 | 186/240 | 53 | 0 | 0 | 1 | 0 | 0 | 198/240 of 240 |  |
| p167A5 | 167.2[0:177] | 5 TL RICHI-177 (RICHI) | 177 | 177 | 131 | 130/177 | 47 | 0 | 0 | 0 | 0 | 0 | 160/177 of 177 |  |
| p169A3 | 169.2[0:184] | 3 TL RICHI-204 (RICHI) | 204 | 184 | 184 | 183/184 | 0 | 0 | 0 | 1 | 0 | 0 | 64/184 of 184 |  |
| p169B2 | 169.4[0:186] | 2 TL RICHI-186 (RICHI) | 186 | 186 | 145 | 145/186 | 41 | 0 | 0 | 0 | 0 | 0 | 40/186 of 186 |  |
| p170D | 170.5[0:187] | RICHI-190 (RICHI) | 190 | 187 | 188 | 187/188 | 0 | 1 | 0 | 0 | 0 | 0 | 187/0 of 187 | hdr [10, 11] vs page [9, 11] |
| p173A | 173.0[0:106] | RICHI-106 (RICHI) | 106 | 106 | 106 | 106/106 | 0 | 0 | 0 | 0 | 0 | 0 | 106/0 of 106 |  |
| p174A3 | 174.1[0:261] | 2 TL RICHI-252 (RICHI) | 252 | 261 | 257 | 252/262 | 5 | 0 | 0 | 4 | 1 | 0 | 261/261 of 261 | hdr [10, 11] vs page [9, 11] |
| p175E | 175.6[0:242] | RICHI---- (RICHI) | None | 242 | 242 | 241/242 | 0 | 0 | 0 | 1 | 0 | 0 | 162/242 of 242 |  |
| p177A3 | 177.2[0:79] | 3 TL RICHI-98 (RICHI) | 98 | 79 | 74 | 74/79 | 5 | 0 | 0 | 0 | 0 | 0 | 40/79 of 79 |  |
| p179A | 179.0[0:214] | 4 TL RICHI-224 (RICHI) | 224 | 214 | 214 | 214/214 | 0 | 0 | 0 | 0 | 0 | 0 | 79/214 of 214 |  |
| p179A6 | 179.2[0:160] | 6 TL RICHI-160 (RICHI) | 160 | 160 | 80 | 80/160 | 80 | 0 | 0 | 0 | 0 | 0 | 80/160 of 160 |  |
| p185A | 185.0[0:55] | RIZI-74 (RIZI) | 74 | 55 | 40 | 38/55 | 15 | 0 | 2 | 0 | 0 | 0 | 40/0 of 55 | letters INT |
| p185C | 185.2[0:49] | RIZI-56 (RIZI) | 56 | 49 | 49 | 49/49 | 0 | 0 | 0 | 0 | 0 | 0 | 49/0 of 49 |  |
| p186D | 186.3[0:37] | RIZI-27 (RIZI) | 27 | 37 | 37 | 37/37 | 0 | 0 | 0 | 0 | 0 | 0 | 37/0 of 37 |  |
| p187C3 | 187.6[0:108] | 3 TL RICHI-108 (RICHI) | 108 | 108 | 103 | 103/108 | 5 | 0 | 0 | 0 | 0 | 0 | 108/108 of 108 |  |
| p189B3 | 189.3[0:242] | 2 TL RICHI-242 (RICHI) | 242 | 242 | 236 | 235/243 | 7 | 1 | 0 | 0 | 0 | 0 | 200/0 of 242 |  |
| p190B | 190.2[0:140] | 1 TL RICHI-214 (RICHI) | 214 | 140 | 140 | 140/140 | 0 | 0 | 0 | 0 | 0 | 0 | 40/140 of 140 |  |
| p190G | 190.3[0:134] | RICHI-134 (RICHI) | 134 | 134 | 135 | 134/135 | 0 | 0 | 0 | 0 | 1 | 0 | 54/134 of 134 |  |
| p192A | 192.0[0:90] | RIZI-46 (RIZI) | 46 | 90 | 90 | 83/90 | 0 | 0 | 7 | 0 | 0 | 0 | 90/0 of 90 | hdr [13, 11] vs page [14, 11]; letters RU |
| p194A.2 | 194.1[0:186] | 2 TL RICHI-186 (RICHI) | 186 | 186 | 186 | 186/186 | 0 | 0 | 0 | 0 | 0 | 0 | 186/0 of 186 |  |
| p196B | 196.1[0:195] | RICHI--- (RICHI) | None | 195 | 195 | 195/195 | 0 | 0 | 0 | 0 | 0 | 0 | 195/0 of 195 |  |
| p197D1 | 197.3[0:45] | 1 TL RICHI-214 (RICHI) | 214 | 45 | 45 | 45/45 | 0 | 0 | 0 | 0 | 0 | 0 | 40/0 of 45 | hdr [16, 11] vs page [14, 11] |
| p200C | 200.3[0:185] | RIZI-190 (RIZI) | 190 | 185 | 185 | 184/185 | 0 | 0 | 0 | 1 | 0 | 0 | 185/0 of 185 |  |
| p201A | 201.0[0:247] | RICHI-244 (RICHI) | 244 | 247 | 236 | 229/247 | 11 | 0 | 7 | 0 | 0 | 0 | 241/247 of 247 | letters NTU |
| p201D | 201.3[0:165] | CHI-170 (CHI) | 170 | 165 | 165 | 165/165 | 0 | 0 | 0 | 0 | 0 | 0 | 40/165 of 165 |  |
| p201E | 201.4[0:147] | RIZI-142 (RIZI) | 142 | 147 | 147 | 146/147 | 0 | 0 | 1 | 0 | 0 | 0 | 0/147 of 147 | letters K |
| p207_2 | 207.3[0:242] | 2 TL RICHI-282 (RICHI) | 282 | 242 | 242 | 242/242 | 0 | 0 | 0 | 0 | 0 | 0 | 40/242 of 242 | hdr [18, 11] vs page [16, 11] |
| p213D | 213.4[0:116] | RICHI-116 (RICHI) | 116 | 116 | 110 | 110/116 | 6 | 0 | 0 | 0 | 0 | 0 | 0/116 of 116 |  |
| p215A2 | 215.1[0:160] | 2 TL RICHI 284 (RICHI) | 284 | 160 | 160 | 160/160 | 0 | 0 | 0 | 0 | 0 | 0 | 160/0 of 160 |  |
| p215A.3 | 215.3[0:197] | 4 TL (Missed start) (None) | None | 197 | 197 | 197/197 | 0 | 0 | 0 | 0 | 0 | 0 | 197/0 of 197 |  |
| p218A | 218.0[0:390] | RICHI-392 (RICHI) | 392 | 390 | 391 | 390/391 | 0 | 1 | 0 | 0 | 0 | 0 | 390/0 of 390 | hdr [23, 11] vs page [22, 11] |
| p218B1 | 218.1[0:145] | RICHI-220 1 TL (RICHI) | 220 | 145 | 160 | 144/160 | 0 | 0 | 0 | 0 | 1 | 15 | 125/0 of 145 | hdr [23, 11] vs page [22, 11] |
| p218B3 | 218.3[0:219] | 3 TL RICHI-234 (RICHI) | 234 | 219 | 219 | 218/219 | 0 | 0 | 0 | 1 | 0 | 0 | 219/0 of 219 | hdr [23, 11] vs page [22, 11] |
| p218C | 218.4[0:248] | RICHI-248 (RICHI) | 248 | 248 | 248 | 247/248 | 0 | 0 | 0 | 0 | 1 | 0 | 248/0 of 248 |  |
| p220B | 220.5[0:204] | 1 TL RICHI-204 (RICHI) | 204 | 204 | 204 | 204/204 | 0 | 0 | 0 | 0 | 0 | 0 | 40/204 of 204 |  |
| p220C | - |  () |  | 0 | 6 | 0/6 | 0 | 0 | 0 | 0 | 0 | 6 | 0/0 of 0 |  |
| p222C | 222.3[0:284] | RICHI-394 (RICHI) | 394 | 284 | 284 | 284/284 | 0 | 0 | 0 | 0 | 0 | 0 | 284/0 of 284 |  |
| p231B2 | 231.2[0:264] | 2 TL RICHI-264 (RICHI) | 264 | 264 | 230 | 230/264 | 34 | 0 | 0 | 0 | 0 | 0 | 264/0 of 264 | hdr [1, 12] vs page [30, 11] |

## Order of work, and what creilly data I saw before the blind commit

The blind commit is `95ceb08`, made 2026-11-01 01:07:39 EDT. Here is everything
from creilly's records that was read before it.

- **Fields with no symbols** (2026-10-31): ids, pages, dates, headers and parts of all records,
  plus the status and method of the Solved rows. I used them to build the work list and to see
  how ids map onto pages.
- **Symbols of three non-target entries, plainly disclosed.** At the very start, while
  inspecting the records schema and before any page image was viewed, I printed the full records
  of **p072B3, p073A1 and p073A2**, including `printed`, `ciphertext` and `plaintext`.
  - None of the three is an Unsolved or calibration id.
  - Their pages, 72 and 73, also hold Unsolved ids (p072A, p072B1, p073B). Those pages were
    transcribed by a reader agent that never saw this output.
  - I adjudicated nothing on pp. 72–73 before the blind commit. The pre-commit adjudications are
    on pp. 102–222 and are listed in `scan-raw/adjudication/`.
  - I did read four lines of **p072A** myself, from the image, to seed the OCR templates. I had
    not seen creilly's reading of p072A.
- **The `compare_*.py` scripts** compare reader with OCR, and reader with reader. They read no
  creilly data.
- **No creilly comparison ran before the blind commit.** `map_and_diff.py` and `calib_truth.py`
  were written before the blind commit and first run after it. `map_and_diff.py` was then
  replaced by `map_spans.py` and `final_diff.py`.

## Net indicator per entry

Each entry has the field `net_indicator`: the call/net indicator as printed in its block label,
e.g. `RICHI-240`, `CHI-170`, `RIZI-46`.
- A count typed as dashes or with a "?" is kept as printed (`RICHI-----`, `RICHI-164?`).
- A label printed over several lines keeps all its parts: p071A2 is `CHI-186 / RICHI-186`.
- `net` gives the bare net (RICHI / RIZI / CHI).
- 80 of the 83 have one. p148A's label column is a dash run, p215A.3 is labelled
  "4 TL (Missed start)", and p220C is not on the page.

## What I could not establish

- **A second, independent transcriber.** Readers 1 and 2 and the adjudicator are all agents of
  one team, using one protocol. So this is not [C]. A human reading of the 238 unchecked
  symbols, and of the 8 ambiguous columns, would be the cheapest next step.
- **The 8 ambiguous glyphs:**
  - p087C trailing specks;
  - p125B `VXFVX` (blot);
  - p157A2 `VDFDVD`;
  - p174A3 `GXVGG`;
  - p190G mark after `FFDXX`;
  - p218B1 `XVAVG`;
  - p218C `FDDFX`;
  - p195A.2 (calibration).
  - Both readings are recorded. The key, once found, decides them, not the image.
- **The length of printed gaps** ("(INTERFERENCE)", "(and several groups Missing)", "(missed 20
  groups)"). The page does not print it. The header count bounds it only if the count is
  trusted.
- **What a parenthesised symbol, a W in one cell, and a dot or hand stroke before a group meant
  to Childs.** We transcribe them; we do not interpret them.
- **The OCR has no templates for letters outside ADFGVX, or for parentheses.** It cannot confirm
  those, so they rest on the readers alone (two readers on the 24 hard pages).

## Reproduce

All scripts are in `ciphertexts/adfgvx-1918-scan-tools/`. Python is
`~/dev/projects/ciphers/.venv/bin/python -I`. The PDF goes in `$TMPDIR/pdf/childs.pdf`.

    ocr_run.py OUT.json PAGE...                        # OCR (reproduces the run used, byte-identical on 6 sampled pages)
    compare_groups.py scan-raw/readers1 OCRDIR OUT     # OCR vs reader 1
    compare_readers.py scan-raw/readers1 scan-raw/readers2 OUT
    build_blind.py scan-raw/readers1 scan-raw/adjudication CMP_OCR CMP_RD ciphertexts/adfgvx-1918-scan-blind.json
    map_spans.py BLIND RECORDS WORKLIST OUT            # after the blind commit only
    final_diff.py BLIND RECORDS SPANS OVERRIDES OUT
    calib_truth.py REPO OUT ; calib_score.py TRUTH FINAL_DIFF OUT
    build_final.py REPO                                # writes the transcription JSON

The raw OCR per page (9.4 MB) is not committed: it is regenerated by `ocr_run.py`.
