# Literature: the open WWI ADFGVX messages (Childs 1918 log)

lit-adfgvx, 2026-10-31. Requested by `dev` for `lead-adfgvx`. **R** = READ (fetched and read by
this chat or its subagent, on the date given). **C** = only seen cited. No decryption was
attempted. The ciphertext alignments in §1.3 and §3 are transcription comparisons from a single
implementation. They are leads, not [C].

## Headline

1. **Most of the brief's target list has been taken already.** Schmeh's nine "open" messages
   were (Childs pp.) 73, 152, 153 ×2, 158, 170, 176 GGDAA, 189 and 198. Public claims now cover six:
   - **153 ×2: claimed solved.** They are parts 5 and 6 of one message, solved under a new
     18-column key.
   - **176 GGDAA: claimed solved.** Known key nov10, with a 20-symbol gap filled.
   Both claims are by creilly11235/adfgvx-1918 (Oct 2026).
   - **158: claimed a log "chimera"** of p.159 B/C.
   - **152 and 189: claimed duplicate intercepts** of messages already solved (0wwafa issue #1,
     28 Oct 2026).
   - **No claim against 73, 170 or 198.** None of these claims is refereed.
2. **The real pool is about 83 entries, not 9.** creilly transcribed the whole of Childs's
   Appendix B from the free scan: 688 entries, 83 of them "Unsolved", about 13,750 symbols. The
   transcription is saved in `literature/adfgvx-transcriptions/creilly-childs-log-688.json`.
   Schmeh's 22 is the 2017 subset Lasry chose.
3. **The mutilation model is published.** See Lasry's thesis §6.5 (READ) and the 0wwafa error
   table (READ), in §2 below. Lasry's repairs were picked by eye with no null. That is where a
   rigorous new contribution is still possible.
4. **The primary source is free and was read here.** It is a 248-page scan of Childs's Aegean
   Park book. Pages 73, 170 and 198 were viewed. New facts from the scan:
   - p.198 is a **CHI-170** message, not RICHI, and its header count is 170 against 165 symbols
     received.
   - p.73 is **POT v NKJ, 8 Nov**, filed under 26 Oct.
   - p.170 has no call signs and a handwritten count.
5. **Novelty, in brief.** A known-key reading of 153, 176 GGDAA, 152 or 189 would be **known**
   (claimed). One of 73, 170 or 198 would be **new as far as searched**. A new key is new only if
   it is absent from the 22 keys listed in §2.3. A negative exclusion is **partially known**
   (0wwafa §5.3, Bourdeau): a null-calibrated, exhaustive one would add rigour, not a new fact.

## 1. Status today (2026-10-31)

### 1.1 Sources checked

| Source | What it says about the open set | R/C, date |
|---|---|---|
| Schmeh, "Unsolved ADFGVX messages from World War I" (scienceblogs.de, 2017), Lasry's list of 22 | The base list; no later annotations | R (via saved copy), 2026-10-31 |
| Schmeh, klausschmeh.net/adfgvx-top-50-cipher-mystery-solved-by-aiwwi/ (2026-09-21) | p.217 solved: "prinz", GPT-6 Astra, keyword TRUPPENVERSCHIEBUNG, "EIN ENGLISCHER KREUZER EINLIEG X SEWASTOPOL …". No other message. Comments: Hongki Min (21 Sep) claims a "breakthrough" on EF-01…EF-21 (keywords OITOS, EINRUECKE, a 20-column key, "slip offsets"); Jozef Krajcovic (22 Sep) disputes it point by point (circular anchors, an undefined slip model, a benchmark missing the claimed substrings). No follow-up | R, 2026-10-31 |
| Bourdeau, dbourdeau.github.io/cyphersolver/adfgvx.html (updated 2026-10-26) and repo targets/adfgvx/NOTES.md (HEAD 89c70be0, 2026-10-31) | Still lists 73, 152, 153 ×2, 158, 170, 176 GGDAA, 189 and 198 as open. Failed attacks are listed in §2.4 | R, 2026-10-31 |
| **creilly11235/adfgvx-1918** (Colin Reilly with Claude; commits 2026-10-11 to 10-26, HEAD e60da03) | Full-log transcription and status (688 entries). Claims 153 ×2 and 176 GGDAA solved and 158 a duplicate (details in §1.2) | **R**, 2026-10-31 |
| **0wwafa/adfgvx-1918** (Robert Sinclair, 2026-09-20; fork lmchdev/adfgvx-1918) docs/PAPER.md | Independent re-verification of the 12 read messages. Systematic error-model search. **Negative results for the remaining ten under 16 keys** (§5.3) | R, 2026-10-31 |
| 0wwafa/adfgvx-1918 **issue #1** (AyushAg1002, 2026-10-28, open, "provisional", AI-assisted, "not yet checked against the Childs page images") | p.152 is a repeat of solved p139B. p.189 is a damaged copy of solved p188_.2 ("Gestellung Auto unmöglich. Befehl abwarten. I.V. Rente."). Says 25 'unsolved' log entries are second intercepts. Proposes readings of p0924 pt 2, p110D, p190G, p072A, p125B (part) and p189B3 (part) | R, 2026-10-31 |
| kajoty/adfgvx-reconstruction (2026-09-27) | Schmeh's 22 checked against the PNG clips on Schmeh's page; header readings. Nothing solved beyond 2017 + 217 | R (README, docs), 2026-10-31 |
| Mqsirrel/adfgvx-1918-cipher-solution, Mqsirrel/astra-crypto-toolkit (2026-09-19) | Re-derive p.187 (CHI) only, which was already solved in 2017 | R (README), 2026-10-31 |
| swarm-ai-research/cipher-break-verification (2026-09-17) | Independent re-check of the p.217 claim, from the archive's ciphertext | R (README), 2026-10-31 |
| Tomokiyo, Cryptiana unsolved list (cryptiana.web.fc2.com/code/unsolved.htm) | No ADFGVX or Childs entry. The list is early-modern; it mentions Lasry's 56 AI solutions (10 Oct 2026), all BnF items | R (keyword scan of the full page), 2026-10-31 |
| Lasry's own statements on the 2026 wave | None found on ADFGVX. Bourdeau reports Lasry reviewed his 88 solves (Schmeh 2026-10-11, see `short-ciphers.md`) | Searched, nothing, 2026-10-31 |
| News on p.217 (cyberkendra, sesamedisk, pasqualepillitteri, theneuron, runtimewire, braindetox.kr …) | All trace back to prinz's 17 Sep post. No other message | C (search snippets), 2026-10-31 |

### 1.2 The nine, one by one

Ids are creilly's: `p` + PDF page + log letter. The PDF page is the Childs page + 3.

| Childs p. | id | Claimed status, by whom, when | Evidence offered | Our view |
|---|---|---|---|---|
| 73 | p076A | **Unsolved** everywhere | — | Open |
| 152 | p155E | **Duplicate of solved p139B**, last 104 symbols (Ayush, 2026-10-28) | 88/102 readable symbols agree at a fixed offset | Our check: 88/104 agree at offset 210 of p139B (314 symbols); chance is about 17. **Strong**: a repeat, not a cryptogram to attack |
| 153 VFVAX | p156C3 | **Solved**, part 5 of FKR v CGH, new key `16 7 13 4 15 8 17 3 1 12 14 2 5 9 10 18 11 6` (creilly, 2026-10-11) | Score −266.7 against −283.4 for the next key and −301.1 max over 10 shuffles. 10/24 planted controls recovered. An independent second run found the same order. Recovers p.187's CHI key blind. 220/225 symbols re-encrypt | Credible, unrefereed. **Not ours to claim** |
| 153 AXVAA | p156C6 | **Solved, 3 letters open**, part 6 of the same message, same key; two symbols corrected A→X | as above | as above |
| 158 | p161D | **"Duplicate entry: a log chimera of the entries on page 159 B and C, not a cryptogram"** (creilly) | Not argued in detail | Our check: 117/241 agree with p162B (unsolved, 280) at offset 5. Partly a duplicate. Schmeh's text of p.158 also differs from the scan (§3) |
| 164 ×2 | p167A, p167A5 | Partial (Norbert, 2017) | 2017 comments | Partial |
| 170 | p173A | **Unsolved** everywhere | — | Open |
| 176 GGDAA | p179B1 | **Solved, 6 open**: message 2305 part 1, key nov10 (Lasry), 4 groups lost at symbol 160 and filled by DP (creilly, 2026-10-11) | Gap placement takes 99% posterior over 194,756 placements. 54/60 planted gaps located. Shuffles score −3.45…−4.05 per letter against −2.11. Place names absent from the scoring corpus | Credible, unrefereed. **Not ours to claim** |
| 189 | p192A | **Duplicate of solved p188_.2, read** (Ayush, 2026-10-28) | 63 matches against 16 mismatches, gap-aware | Our plain fixed-offset check: 52/90 at offset 0; chance is about 15. Consistent |
| 198 | p201D | **Unsolved** everywhere | — | Open. **CHI-170**, see §3 |
| 215 VGADA | p218C | Partial (Norbert, Baertl 2017). Bourdeau: 20 of Baertl's 129 letters contradict the received cells | | Partial |

**Hongki Min** (Schmeh comment, 2026-09-21): unverified self-report. It uses its own "EF-01…21"
labels with no Childs page numbers, and was challenged the next day with no answer. Status
**claim, not established**. We would not count anything from it.

### 1.3 Who has been where, and when (the trials factor)

- **2017.** Comment thread: Norbert, Armin, Thomas, Baertl and Lasry, "add or remove up to 5
  characters at two different positions, exhaustive search with an n-gram value function"
  (Norbert, comment 23). Saved in `adfgvx-transcriptions/schmeh-2017-comments-via-kajoty.txt`.
- **Sep 2026.** prinz (p.217). Bourdeau: two-block-edit search, 15 keys × 10 open messages; a
  keyless attack failed on a planted 224-letter control. 0wwafa: 16 keys, methods 1–7 (two- and
  three-edit search, beam, column-offset annealing, interim-text edits, key variants, unknown-key
  annealing, K = 15…23). kajoty. Hongki Min.
- **Oct 2026.** creilly: full log, known-key + gap DP, an even-length-key unknown-key attack, and
  the p.153 key tested against 40 other unread messages from 6–9 Nov. Ayush: duplicate detection
  over the whole log, plus random-key controls.
- Anything the team finds among these messages must beat the best of all of the above. In
  particular, 73, 170 and 198 have already failed every published key under ≤7 edits (0wwafa
  §5.3: no candidate above −5.5, where genuine decrypts score −4.0 to −4.8).

## 2. The prior work in detail

### 2.1 Lasry, Niebel, Kopal, Wacker (2017) and Lasry's thesis (2018)

- **Paper: C.** Cryptologia 41(2):101–136, 2017, doi:10.1080/01611194.2016.1169461. Behind a
  paywall, not read.
- **Thesis: R** (subagent, 2026-10-31). G. Lasry, *A Methodology for the Cryptanalysis of
  Classical Ciphers with Search Metaheuristics*, kassel university press 2018, ISBN
  978-3-7376-0458-1, open access (uni-kassel.de/upress/online/OpenAccess/978-3-7376-0458-1.OpenAccess.pdf).
  Ch. 6, "Case Study – The ADFGVX Cipher", pp. 83–112, states that it contains the paper's results.

**Corpus (§6.1, p. 84).** 460 messages and 668 cryptograms (repetitions excluded), Sep 19 to
Dec 7 1918. Mean 215 symbols, range 36–500.

**Method (§6.4, pp. 91–94).**
- Transposition first, by hill climbing over batches of cryptograms thought to share a key.
- Moves: swaps, segment swaps and rotations, reversal, adjacent-pair swaps.
- Score: **ICpairs**, the IC of adjacent symbol pairs after undoing the transposition. For even
  key lengths it is combined with **ICquads**.
- Then the substitution, as a monoalphabetic hill climb.
- Key length is tried over 15–25. The recovered keys were 16–23 long.

**Data needed (Table 6.1, p. 94).**
- 2 cryptograms (388–566 symbols) were enough for 6 of the 14 keys.
- The worst case was 5 cryptograms (1,000 symbols) for a length-18 key.
- The smallest success was 388 symbols at length 16.
- Bourdeau's "356 letters for length 16" is **not** in the thesis. Treat it as Bourdeau's own
  figure.
- §6.5.2 says the attack is robust to up to 20% of cryptograms not belonging to the key.

**Keys (Table 6.2, p. 99).** 14 keys:
- Sep 19–21 and Oct 4–6, 22 columns.
- Oct 28–31, 18.
- Nov 1–3, 19.
- Nov 4–6, 17.
- Nov 7–9, 20.
- Nov 10–12, 16.
- Nov 13–15, two keys: 20 and 16 columns.
- Nov 16–18, 19.
- Nov 19–21 (new), 20.
- Nov 22–24 (new), 22.
- Nov 25–28 (new), 23.
- Nov 28–Dec 1 (new), 16.

Eight agree with Childs's keys. Childs's Nov 4–6 transposition lacks an element, and his Oct 4–6
square has two rows swapped (p. 98). Errata in the thesis: the Sep 19–21 key prints "2,2,…" for
"12,2,…", and Fig. 6.2's Nov 7–9 square has N twice. **There is no key for 7–27 Oct.** The 26 Oct
page (p.73) falls in that gap.

**Results (§6.5, pp. 95–98).**
- 618 of 668 read.
- About 400 read cleanly. Many cryptograms were "wrongly placed in the logs" and read under
  another day's key.
- About 250 needed repair: about 110 minor, about 34 of the right length with many hyphens, and
  27 of the wrong length but recovered.
- **50 failed.** 36 had too many groups missing. 14 had the right length but fitted no key,
  "probably wrongly encrypted".
- The failures are **not listed** by message, here or (per creilly) anywhere else.

**Mutilation, i.e. what the team's model must cover (§6.5.1, §6.5.3).**
- "About one third of the cryptograms have either an incomplete transcription or have
  transcription errors"; "almost all of them had garbled letters" after decryption.

Visible error types:
1. Hyphens. Operators were told not to guess, so whole groups could be hyphenated.
2. 3-, 4- or 6-symbol groups.
3. Letters outside ADFGVX, such as U or B.
4. Missing segments, usually at the start or end, with notes such as "jammed" or "interference".
5. The length received does not match the length sent in clear.
6. An odd length sent in clear.

Repairs:
- A hyphen whose partner symbol is known leaves 6 candidates.
- A 4-symbol group: a hyphen tried in each of the 5 positions.
- A 6-symbol group: each of the 6 symbols tried as the deletion.
- Excess length: symbols trimmed from the start or end, then from every location.
- Short length: hyphen groups inserted "at various positions", keeping the best plaintext.
  This was manual and recovered 27 messages.
- **No significance test.** Choices were made by eye.

**Not described anywhere:** group transpositions, operator wrong-key use, or per-symbol error
rates. No rates are given.

### 2.2 The error model as later formalised

0wwafa PAPER.md §3 (R) lists:
- **E1** symbols dropped.
- **E2** symbols doubled or inserted.
- **E3** whole group dropped or duplicated.
- **E4** unreadable symbol.
- **E5** Morse substitution.
- **E6** the clerk encoding one letter with 3 symbols (p.132: `VVV` for `VV`; Norbert 2017,
  comment 37).
- **E7** logged under the wrong day.
- **E8** a key not in the list (CHI traffic, out-of-period keyword).

"E1–E3 are the dominant cases." The paper calibrates its own scorer: genuine decrypts score −4.0
to −4.8 (mean log10 quadgram), random text about −8.1, and the noise floor of a wrong-key
two-edit search −6.4 to −6.7.

Worked repairs on the 2017 solves, as calibration data:
- p.100: insert 2.
- p.105: two deletions.
- p.109: a duplicated pair of groups.
- p.132: E6.
- p.146: a group inserted and two groups merged.
- p.171: seven single-symbol edits.
- p.176a: a group inserted and two groups rewritten.
- p.215: two group insertions.
- p.187 and p.217: no edits at all; the key was the problem.

creilly's statistics are the best quantitative input available: 550 solved entries, each with its
exact repair, in `data/records.json` / `messages.json` upstream. Not copied here beyond the slim
extract, because they are someone else's results. The team can derive empirical edit-type rates
from them, with credit.

### 2.3 The keys that exist (22, per creilly data/keys.json, R)

- Lasry's 14.
- Five 1918 keys from Childs's book and Appendix C: Jul 18, Jul 22, Aug 3, Aug 8 and Aug 20 (out
  of period).
- dec09_history (TRUPPENVERSCHIEBUNG, Childs's 1919 history).
- chi_2017_comments: Lasry's CHI key of 13 Nov, `3 13 2 12 1 11 15 8 9 4 5 14 6 10 7 16`.
- ours_nov07_18col: creilly's p.153 key.

0wwafa's negative results used **16** (14 + CHI + TRUPPENVERSCHIEBUNG). **The five Jul–Aug Childs
keys were not in its exclusion.** Bourdeau used 15. Whether creilly tried all 22 on 73, 170 and
198 is not stated.

### 2.4 Bourdeau (R, adfgvx.html updated 2026-10-26; NOTES.md)

- Keyless attack: **failed on a planted 224-letter control** under a length-19 key.
- Two-block-edit search over 15 keys and 10 open messages: nothing above the solved-message
  threshold.
- CHI key on both p.153 parts: noise. This is now explained: they use another key, per creilly.
- His table still shows 153, 158 and 176 GGDAA as open. **It is out of date** relative to creilly.

### 2.5 Childs and the archive

**Childs book: R.** J. Rives Childs, *General Solution of the ADFGVX Cipher System*, Aegean Park
Press c-88 (2000/2002; Bean flags the date as uncertain).
- Free scan via Richard Bean's index (richardbean.id.au/misc/kryptos/aegean-park-press.html,
  reviewed 2026-09-07). It is a Google Drive PDF of 248 pages, sha256 `157e41a1…798ad06`,
  downloaded 2026-10-31.
- Appendix B holds the logs; Appendix C the keys.
- Pages viewed here: 73, 170 and 198 (PDF 76, 173, 201).

**Other Childs material (R through creilly SOURCES.md, C for the documents themselves).**
- *German Military Ciphers from February to November 1918* (1935, NSA-declassified 2014; NSA
  Friedman collection FOLDER_268).
- 1919 history, *The History and Principles of German Military Ciphers 1914–1918* (a 218-page
  scan at the National Cryptologic Museum).
- NCM bundle DKP005 016.
- Moorman's *Final Report of the Radio Intelligence Section*.
- Friedman 1934, *General Solution of the ADFGVX Cipher System* (NSA FOLDER_269).

**Unopened archive leads (creilly SOURCES.md, R).**
- NARA RG 120 Entries 104–106.
- UVA Childs papers, Accession 9256-b Box 14.
- NCM DK 055 069.
- TNA HW 7/35, HW 3/176–182.
- SHD Vincennes GR 19 N 1416–1418 (French cipher-section grids and deciphering reports).

A second intercept of an open message (British or French copy) would be the strongest way to
settle it. Lasry's thesis says most intercept material was not preserved.

### 2.6 creilly11235/adfgvx-1918 in full (R, README and scripts @ e60da03, 2026-10-31)

**Data.**
- All 688 log entries, transcribed from the free scan.
- 22 keys, listed in §2.3. Five cells of Lasry's nov10 square are blank; they were filled with
  the digits 5–9, following a 2017 Schmeh commenter.
- Each entry records the printed text, the repaired text with edits in lowercase, the key, the
  reading, a confidence and a credit.
- `scripts/verify_all.py` re-decrypts every stored reading and re-encrypts it. For unedited
  intercepts it demands an exact round trip.
- **The search code is "not packaged".** Only the cipher, the verifiers and the page builders are
  in the repo. Their searches cannot be re-run from the repo.

**Scoring.**
- Natural-log 5-gram counts from **the 544 already-read messages of the collection** plus ordinary
  German books.
- Caution for anyone reusing it: an in-corpus language model favours stock telegram phrases.
  creilly's own guard against that is out-of-corpus words (PETERREVE, VERSECZ, VON SERBEN, the
  216th Division), which their scoring text did not contain.

**Gap fill (p.176 GGDAA, message 2305 part 1).** The header says 240 symbols; 220 were received.
1. **Placement.** All placements of the 20 missing symbols were enumerated: one block of 20, or
   four separate groups of 5, giving **194,756 placements**. Each placement was scored with the
   gaps as known unknowns.
2. **Filling.** Each half-lost letter has 6 candidates, from the row or column of the surviving
   symbol. 6^20 fills were scored exactly by **dynamic programming** over the 5-gram model, giving
   the best fill, the runner-up and per-letter posteriors.

| Gap fill result | Value |
|---|---|
| Winning placement | One block at symbol 160, i.e. the first half of the fifth log line |
| Lead over next placement | 5.9 nats (×370) |
| Posterior on the winner | 99% |
| Null: 12 wrong keys, shuffled symbols, or shuffled known letters | Best fill −3.45 to −4.05 per letter |
| Real message | −2.11 per letter |
| **Planted control** | 60 read messages with 20 symbols deleted each; gap correctly placed in **54/60**; median score −2.09 |
| Re-encryption | All 220 received symbols come back (a consistency check only, which they say themselves) |

**New key (p.153, two parts: 132 + 108 symbols, 15 lost, about 120 letters).** For an
even-length key, each column holds only row labels or only column labels. Their symbol mixtures
therefore separate into two classes before anything else about the key is known.
1. Enumerate column-length splits per part, and keep those whose columns cluster cleanly into the
   two classes.
2. Pair row-label columns with column-label columns and order them, ranking by the IC of the
   letter stream.
3. Hill-climb the square: a short run for all candidates, then a long run for the best 200.

| New key result | Value |
|---|---|
| **Planted control** | 24 messages of the same geometry (66 + 54 letters, 15 lost) under random 18-column keys; exact key recovered **10/24**; every exact recovery scored ≥ −268.0 |
| Real pair | −266.7 |
| Next distinct key | −283.4 |
| **Null**: 10 shuffled copies | Best −301.1 |
| Blind positive control | p.187 CHI pair: returned Lasry's key and his 22 square cells, −283.4 against −429.0 for the next key |
| Second, independently written run (also Claude) | Same column order; squares agreed on 17/25 cells compared; the rest settled by repeated words |
| Specificity | Key opens none of 40 other unread 6–9 Nov messages; none of 19 published squares fits p.153 at widths 15–25 |
| Edits needed | Two A→X log corrections; 12 lost letters filled by reading; 3 left open |
| Re-encryption | 220/225 surviving symbols |

**Trials factor (our assessment).**
- The shuffled null (10 copies) is small, and its margin of 34 log units is large.
- The 10/24 planted recovery rate means a failure on another message says little.
- They do not give an explicit count of methods and variants tried before success.

**Bulk status (550 solved).** "Solved" means every surviving symbol decrypts and the text reads as
German. Repairs are published only "where a repair could be scored against shuffled copies of
itself". Leads, eye-read repairs and rows whose log differs from the print are withheld, so
"Unsolved" means only "not published here".

**Lessons the team can use.**
- p.176 GGDAA fell to a **20-symbol block gap** under a known key.
- 0wwafa's ±6-symbol edit window (below) could not reach it, and 0wwafa wrongly diagnosed it as
  "wrong encryption".
- So: **check each header count against the symbols received** before inferring wrong encryption.
  p.198 is short by exactly 5 (one group).

### 2.7 0wwafa/adfgvx-1918 in full (R, docs/PAPER.md @ 0839217, 2026-10-31)

**Data.** Schmeh's 22 (HTML text, dashes normalised). It does not use the scan.

**Keys.** Lasry's 14 (blank cells restored from his blog comments), plus the CHI key and
TRUPPENVERSCHIEBUNG: **16 in all**.

**Scoring.**
- Mean log10 quadgram over about 3 MB of German prose, **plus a heavily up-weighted corpus of the
  already-solved 1918 plaintexts and military vocabulary**. The same in-corpus caution applies as
  for creilly.
- Unknowns and digits inside a quadgram are penalised at −7.0. An earlier version skipped them
  and the optimiser exploited it.

**Calibration source**, i.e. where the E1–E8 thresholds come from:
- Genuine decrypts of this traffic: −4.0 to −4.8, measured on the 12 read messages of the 22.
- Random text: about −8.1.
- Noise floor of an exhaustive two-edit search under a *wrong* key: −6.4 to −6.7.
- Wrong-key ceiling over all searches of the residue: −5.5.
- **The calibration sample is small** (the 12 read messages), and **no trials factor is stated**
  beyond "about 10⁶ variants per key/message" for `search2`.

**Error catalogue E1–E8** (§3). The types are listed in §2.2. **Source:** "From the solved traffic
I catalogued the failure modes". In practice that means the 2017 hand repairs of the 12 read
messages, matched against Lasry's thesis types. **No frequencies are given.** "E1–E3 are the
dominant cases" is asserted, not counted. E6 rests on one instance (p.132). E7 and E8 rest on
p.187 and p.217.

**Engines (§4.2).**
1. Exhaustive two-edit search, Δ ∈ [−6, +6] at any two positions.
2. Three edits on group boundaries.
3. Six-round beam search, width 60.
4. Column-offset annealing: each column start ±7, N ±6.
5. Single deletions in the interim, pre-transposition stream (E6).
6. Key variants: reversed, ±1 element, two columns swapped, all 15×15 transposition/square
   cross-pairings.
7. Unknown-key annealing, K = 15–23, scored by bigram IC.
8. Square constraint-solving from a candidate plaintext, using the conflict count.

**Planted / positive controls (§4.3).** Solutions known but withheld, recovered from the raw
transcription:
- `search2` and beam: p.100, 146, 171, 176a.
- `coldesc`: p.146 (needs ±5 offsets) and p.105.
- Interim search: p.132, with one deletion.
- Unknown-key engine: recovers the K = 16 structure of the 212-symbol p.187, and "nothing stable"
  on 84–178 symbols.
- **No random-key planted messages at the residue's lengths** were run, unlike creilly and
  Bourdeau.

**Negative results (§5.3).**
- All 16 keys × methods 1–7 on the ten residue messages: nothing above −5.5.
- The p.189 fragment at −4.6 needed 12+ columns at ±7 offsets, which they call an over-fit
  signature.

**Per-message diagnosis**, now partly overtaken:

| Message | 0wwafa's diagnosis | Since then |
|---|---|---|
| p.153 | Another CHI key | Correct: creilly found it |
| p.176b | Wrong encryption | **Wrong**: header gap, solved under the known key |
| p.152, 189 | Too short | Both now claimed to be duplicates |
| p.73 | A late-October key missing from the list | Still open |
| p.198 | Wrong encryption | Unproven: header 170 against 165 received |

### 2.8 0wwafa issue #1 (AyushAg1002, 2026-10-28; R, the issue text only)

- **Duplicate detection.** It reports 25 'unsolved' entries as second intercepts of solved
  transmissions. Coverage is 0.50–1.00, against **≤ 0.071 for 400 random pairs of real
  ciphertexts** (the null).
- **Proposed readings** were "compared with matched random-key controls". The details and the
  scripts are offered but not posted.
- Not checked against page images, by its own statement. **The full list of 25 is not in the
  issue.** The team's own duplicate screen of the 83 should be independent anyway.

## 3. The primary source and the transcriptions

**Saved verbatim** in `literature/adfgvx-transcriptions/` (see the README there).
- Four copies descend from Schmeh's 2017 HTML: Schmeh, Bourdeau, 0wwafa and kajoty. Once
  normalised (each token a 5-group, with en/em dashes as collapsed hyphen runs), Schmeh, Bourdeau
  and 0wwafa are **identical on all 22**.
- creilly is the **only copy taken from the scan**, and the only one covering the whole log.

**Schmeh's text against the scan** (`DIFF-schmeh-vs-scan.md`).

Identical, or differing only where creilly marks a symbol unknown:
- Identical: 73, 109, 132, 146, 153 ×2, 170, 176 GGDAA, 187 pt 2, 198, 217.
- creilly marks unknown symbols that Schmeh prints as letters: 100 (1), 152 (2), 187 (1), 189
  (5), 215 (1).

Real differences:
- **p.105**: 3 symbols (`F`→`D`, `XA`→`DG`).
- **p.158**: 241 symbols on the scan against 232 in Schmeh. Schmeh's bracketed `(VVFGD)` and
  `{VVDAD}` are real repeated groups on the scan. Several other substitutions and insertions.
- **p.164 ×2**: large differences in the hyphen runs.
- **p.176 "missing 10"**: the scan shows 10 hyphens where Schmeh has letters.

Header counts against symbols received:
- **p.198: 170 against 165.** One group short.
- p.176 GGDAA: 240 against 220. This is the gap creilly filled.
- **p.73: 178 = 178**, with 2 unknowns (`D--FX`).
- p.189: header 46 against 90 (an OCR or log oddity).
- p.170: the count is handwritten.

**Read from the scan here (R, 2026-10-31).**
- **p.73** (PDF 76), page heading "26th OCTOBER, 1918", "INTERCEPTED BY BRITISH STATIONS":
  - `A) POT v NKJ (2.33 a.m., November 8th) / FÜR COS GENERAL VON KRESS 0911 (26) / RICHI-178`.
  - The message's own time is **8 Nov**, filed on the 26 Oct page. creilly's header OCR has
    "Et v NKJ"; kajoty reads "PQT".
  - The team should note the two candidate dates: 26 Oct falls in Lasry's key gap; 8 Nov falls
    under nov07.
- **p.170** (PDF 173), 9 Nov: `A) --- v --- (11.24 p.m., November 9th)`. No call signs; the count
  after "RICHI-" is a handwritten figure we could not read at 110 dpi. The ciphertext matches
  Schmeh and creilly (106 symbols).
- **p.198** (PDF 201), 15 Nov: `D) PZU v CM (16.27 p.m., November 15th) 18.45`, indicator
  **CHI-170**, not RICHI.
  - The other entries on that page are RICHI-244 (IWE v KI) and three **RIZI** messages (CM/SY v
    CZ). creilly reads RIZI-190 and RIZI-186 under nov13_16; RIZI-142 is unsolved.
  - The only CHI traffic read so far is p.187 (13 Nov, SU v LP, Lasry's CHI key).
  - So p.198 is probably on a **separate CHI net and key**. It is one group short (170 against
    165) — our inference from the indicator, not a claim anyone has made.
- Not done: an independent full transcription of the scan. The three pages above were checked by
  eye against creilly for the header and the indicator only. Doing the full transcription is a
  job for `verify/` or a `check-` chat; the scan is now known and free.

## 4. A stronger WWI target?

A subagent of this chat searched on 2026-10-31. **Verdict: nothing obviously stronger.** None of
the unsolved WWI traffic we found is longer and cleaner and also has a designer or archival
answer. Instead, **the Childs log itself is bigger than the brief assumed**: about 83 unsolved
entries and about 13,750 symbols (§1.2). We rank that above everything below.

| Candidate | What / where | Why not better |
|---|---|---|
| Bernstorff → Berlin cable, 10 Jan 1917, second text | 430 code groups, probably code 0075 (two-part, about 10,000 groups); NARA RG 59 763.72111/4443, M367 roll 166. Bourdeau write-up Sep/Oct 2026 (R: dbourdeau.github.io/cyphersolver/bernstorff1917.html). No plaintext known; about 82 groups graded from the first part | A codebook reconstruction. It has no null in the ADFGVX sense, so a "reading" cannot be scored for significance. Leads: Lasry, Niebel & Andersson, Cryptologia 45(5) 2021 (C); Lasry & van Kampen, Cryptologia May 2026 on WWI diplomatic codes (C, seen only in a Wikipedia bibliography, unverified) |
| Boyen pigeon message, 30 Jul 1914 | 121 letters, a transposition (Schmeh, R) | One short message under an unknown system: much freedom, many false readings |
| Woodcock Marconi telegram, 1916 | 40 letters, digraphic; Lasry's Playfair attack failed (Schmeh 2019, R) | Too short for significance |
| WWI private postcards | Hobby substitutions (C) | Not comparable |
| Western-front ADFGX/ÜBCHI, naval, Austro-Hungarian, Ottoman, Russian | No published unsolved corpus found (Schmeh Top 50, MysteryTwister listing (partial), Wikipedia list, cryptocellar, Cryptiana) | Nothing to attack |

**Gap.** HistoCrypt 2026 (Amiens, June 2026) had WWI as its theme: 27 papers, NEALT Proceedings 61.
Its table of contents could not be reached (dspace.ut.ee refused the connection). It is the one
place a newly published WWI corpus could sit unseen by this survey.

## 5. Novelty verdicts

Searched: everything in §1.1; GitHub repo search "adfgvx" (updated since Aug 2026; 14 repos, 7
relevant, all read); Schmeh 2017 thread; Lasry thesis ch. 6; Bourdeau site and repo; Cryptiana;
web search (news on p.217). Not searched: Cryptologia since 2017 behind its paywall (gap); the
MysteryTwister forum; the Cipherbrain comment threads after 21 Sep 2026 apart from the p.217 post;
the CrypTool forum.

| Claim the team might make | Verdict | Reference |
|---|---|---|
| Reading p.153 (either part) | **Known** (claimed) | creilly11235/adfgvx-1918, 2026-10-11 |
| Reading p.176 GGDAA | **Known** (claimed) | creilly, 2026-10-11 |
| Reading p.152 or p.189 | **Known**: a repeat or copy of solved messages | 0wwafa issue #1, 2026-10-28; our alignments §1.2 |
| p.158 is not an independent cryptogram | **Known** (claimed) | creilly p161D |
| Reading p.73, p.170 or p.198 with a known key | **New as far as searched.** No claim found. Must beat 0wwafa's 16-key ≤7-edit negative, which this reading contradicts unless it uses a key or repair outside that search (e.g. Childs's Jul–Aug keys, the 26-Oct gap, or a missing group on p.198) | — |
| Reading any of the other ~80 unsolved log entries | **Cannot tell per entry.** Check creilly's row and 0wwafa issue #1 for the entry; Lasry never published his failure list | creilly MESSAGES.md; issue #1 |
| Joint recovery of a new key from several unread cryptograms | Method **known** (Lasry 2017/2018 ICpairs on batches; Lasry's 2017 CHI key from 2 messages; creilly's even-key column-class split, p.153). A **specific new key is new** if it differs from all 22 in §2.3 | §2.1, §2.3 |
| Negative exclusion ("no published key opens X under ≤k edits") | **Partially known**: 0wwafa §5.3 (16 keys), Bourdeau (15 keys, 2 block edits), creilly (p.153 key against 40 msgs). New only in rigour: exhaustive, null-calibrated, all 22 keys | §1.3 |
| An empirical mutilation-rate model of the 1918 traffic | **Partially known.** Error types: Lasry thesis §6.5 and 0wwafa §3. **Rates: none published that we found.** creilly's 550 repaired entries are the data | §2.1–2.2 |

## What could not be established

- The Cryptologia paper itself (paywall); its content is taken from the thesis, which says it
  contains the same results.
- Lasry's list of his 50 failures. Not published anywhere we found; creilly says the same.
- Whether creilly's two solutions are right. Unrefereed; we did not re-run them (not our role).
  Their nulls and controls are described in their README and look adequate, but **no one
  independent has checked them**.
- The handwritten count on p.170 and the "(26)" annotation on p.73.
- Whether Schmeh, Lasry or Bourdeau have seen creilly or issue #1. Neither is mentioned on their
  pages as of 2026-10-31.
