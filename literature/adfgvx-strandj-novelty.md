# Novelty check: the 23 strand-J readings (ADFGVX 1918, Childs Appendix B)

lit-adfgvx-j, 2026-11-01. Requested by `dev` for `lead-adfgvx`. This chat did no part of the
mathematics and did not judge whether any reading is statistically real. It answers one question
per unit: **had someone already published a reading of this entry, and is it the same text?**

**What was checked.** The readings are the rows with `role=="target"` and `above==true` in
`results/adfgvx-J1-targets.jsonl` on `origin/lead-adfgvx` @ f26cded (generated from commit
cd0cd93, 2026-11-01 11:28 UTC). This chat read only the fields `unit`, `argmax`, `edits` and
`plain`. It did not read `search/` or the lead's reasoning.

**Labels.** Every source statement is [L], dated. **R** = READ: fetched and read by this chat or
its subagent, on the date given. **C** = only seen cited or in a search snippet.

## Summary

**4 of the 23 are already read in public, letter for letter. 3 more were claimed in public as
summaries. 16 have no prior public reading that we found.**

| Unit (key) | Childs p. | Prior public reading? | Source, date | Same text? | Verdict |
|---|---|---|---|---|---|
| p062A (sep19) | 59 | not found | — | — | new as far as searched |
| p071A1 (oct04) | 68 | not found | — | — | new as far as searched |
| p071A2 (oct04) | 68 | not found | — | — | new as far as searched |
| **p072A (oct04)** | 69 | **claimed, summary only** | 0wwafa/adfgvx-1918 issue #1, AyushAg1002, 2026-10-28 | **overlapping**: same content ("liaison officer sent to Tiflis with OHL agreement"); no letters posted | partially known |
| p072B1 (oct04) | 69 | not found | — | — | new as far as searched |
| **p0924#1 (nov01)** | 89 | **yes, letter-level** | dbourdeau/cyphersolver issue #181, AyushAg1002, 2026-10-28 13:53Z; reproduced by Bourdeau with his own code the same day | **identical except 2 letters**: 140 of 142 positions where both are known agree | **known** |
| p102A (nov01) | 99 | not found | — | — | new as far as searched |
| p102C (nov01) | 99 | not found | — | — | new as far as searched |
| **p110D (nov01)** | 107 | **yes, letter-level** | cyphersolver #181, 2026-10-28; reproduced by Bourdeau | **identical**: 84 of 84 positions where both are known agree | **known** |
| **p125B (nov04)** | 122 | **claimed in part, summary only** | 0wwafa issue #1, 2026-10-28 | **overlapping**: "radio reply requested concerning employment in the Ministry of Trade / demobilisation" | partially known |
| p139A2 (nov04) | 136 | not found | — | — | new as far as searched |
| p141B.2 (nov04) | 138 | not found | — | — | new as far as searched |
| p142A2+p142A (nov04) | 139 | not found | — | — | new as far as searched. The third part, p142A.2, was read by Lasry et al. (2017) and is different text |
| p153B4+p153B (nov04) | 150 | not found | — | — | new as far as searched |
| p170D (nov07) | 167 | not found | — | — | new as far as searched |
| **p189B3 (nov13_16)** | 186 | **claimed in part, summary only** | 0wwafa issue #1, 2026-10-28 | **overlapping**: "men leaving for home on their own authority; OHL Ia" | partially known |
| **p190G (nov13_20)** | 187 | **yes, letter-level** | cyphersolver #181, 2026-10-28; reproduced by Bourdeau | **identical except 1 letter**: 62 of 63 positions where both are known agree | **known** |
| p194A.2 (nov13_16) | 191 | not found | — | — | new as far as searched. Part 1 of the same log entry (p194A) was read in 2017 |
| p213D (nov19) | 210 | not found | — | — | new as far as searched |
| p218A (nov22) | 215 | not found | — | — | new as far as searched |
| **p218C (nov22)** | 215 | **yes, letter-level, 2017** | Schmeh's Top-50 #46 comment thread: Norbert #32, 3 Mar 2017; Max Baertl, 11 Mar 2017 | **identical** apart from a few garbled letters: same key, same two group insertions | **known** |
| p220B (nov22) | 217 | not found | — | — | new as far as searched |
| p231B2 (nov28) | 228 | not found | — | — | new as far as searched |

What the verdicts mean:
- **Known**: the same text is public, with the same key.
- **Partially known**: a public claim to have read the entry, with matching content, but no
  letters to compare.
- **New as far as searched**: nothing found in the sources listed in §4. That is a statement
  about our search, not about the world.

**Consequences for the team.**
1. **p218C is not new.** It is Schmeh's #17 (VGADA). Norbert read it in 2017 under the same key
   and the same repairs as ours.
2. **p0924#1, p110D and p190G are not new.** Ayush Agarwal posted full keys, repaired
   ciphertexts and plaintexts four days before our run. Bourdeau reproduced all three "letter
   for letter" with independent code (`targets/adfgvx/verify181.py`). Our readings agree with
   those texts except at 3 letters in total (§1.2).
3. **p072A, p125B and p189B3 have a prior claim.** On 2026-10-28 the same author published the
   content in summary, but no letters. At most we could be the first to publish the letters,
   and that would be a weak priority.
4. **Ayush says he holds unpublished "full per-entry sheets"**, and 25 duplicate identifications
   whose list is not public. He also says the novelty question is "with George Lasry". Lasry
   may hold readings of any of the 16. Lasry et al. (2017) read 618 of 668 cryptograms and
   never listed them by entry. That is the largest risk to every "new as far as searched"
   verdict above (§3).
5. **None of the 23 is a duplicate intercept of another log entry** under a fixed-offset
   ciphertext screen, and none repeats an already-published plaintext beyond stock phrases (§2).

## 1. The sources that pre-empt a reading

### 1.1 Schmeh 2017 comment thread: p218C

- **Source.** The comment thread under Schmeh's "The Top-50 unsolved encrypted messages: 46 –
  unsolved ADFGVX cryptograms from World War 1" (scienceblogs.de/klausis-krypto-kolumne,
  2017-02-23). [L] **R**: lit-adfgvx read the saved copy on 2026-10-31
  (`literature/adfgvx-transcriptions/schmeh-2017-comments-via-kajoty.txt`), this chat re-read it
  2026-11-01, and this chat's subagent read the live page by curl on 2026-11-01.
- **Norbert, #32, 3 Mar 2017**, lines 332–364 of the saved copy. "This message uses the key
  from Nov 22-24. After group 6 (D.F..) insert new five-letter group and after group 43 (FDFFX)
  as well." His raw text:
  `ABSXMI.I5XNA6M.LD.XS4NXS4.XN.R.DAKER.SC.XBRINGTENT.N.E FLHTTEZWO.IVI.IONENX.EUSRELAEND.RXENGLXUXF.ATZ.XMITX N..OHLXKOR1S..OSCHX3Y52`
- **Max Baertl, 11 Mar 2017**, line 441. His cleaned reading:
  `ABS X MIDIV 5 X EILMELDG X 24N X 24N X ARMADA KERTSCH X BRINGT ENTENTE FLOTTE ZWO DIVISIONEN X NEUSEELAENDER X ENGL X U X FRANZO X MIT X NUR OHL X KORPS FRISCH X 3Y52`
- **Norbert, #49, 30 Apr 2017**, places it at "Childs page 215 … C) UKS v BSL (08.42 p.m.,
  November 22nd) … RICHI-248 VGADA".
- **Ours** (nov22, `ins5@25,ins5@215`):
  `ABSXMI-I5XNA6M-LD-X-4NXS4-XN-R-DAKER-SC-X-RINGTENT-N-EFLHTTEZWO-IVI-IONENX4IUSRELAEND-RXENGLXUXFRATZ-XMITXN--OHLXKOR1S--OSCHX3Y52`
  The same text. Both readings insert two groups at the same places (Norbert's "after group 6"
  against our position 25, "after group 43" against our position 215). Wherever both are
  readable, the letters are the same, apart from a handful of garbles (`S4N` against `-4N`,
  `.EUS` against `4IUS`, `F.ATZ` against `FRATZ`).
- **creilly** has credited it in `records.json` since commit 945d1b1 (2026-10-17): "Norbert and
  Max Baertl, 2017, in part". Status is still "Unsolved". [L] **R**, 2026-11-01.
- **Bourdeau's audit** of this message: "20 of Baertl's 129 letters contradict the received
  cells". [L] **C** here (reported by lit-adfgvx 2026-10-31 and by this chat's subagent); not
  re-checked.

### 1.2 cyphersolver issue #181: p0924#1, p110D, p190G

- **Source.** dbourdeau/cyphersolver issue #181, "Solution: adfgvx — proposed readings of Childs
  p.89, p.107 and p.187", by AyushAg1002, 2026-10-28 13:53Z, open. [L] **R** by this chat,
  2026-11-01, via the GitHub API.
- **Keys.** Lasry's published period keys, no new key. Nov 1–3 for p0924 and p110D, Nov 13–15 for
  p190G, with square cells left `?` where unknown. The issue gives the repaired ciphertext and
  the decryption letter by letter, plus a German reading and an English translation.
- **Unit mapping.** "p0924, symbols 0–289 of the 548-symbol entry: part 2 of the 01:18 p.m.
  OSM de LP message of 1 November". Our `p0924#1` is the same segment: both plaintexts are 145
  letters.
- **Bourdeau's comment, 2026-10-28 18:19Z.** "We decrypted all three with our own code, not
  yours (`targets/adfgvx/verify181.py`) … The output matches your decryptions letter for letter."
  He records it in `targets/adfgvx/NOTES.md` as "a mechanical reproduction on the typed log,
  with credit to you". Two points he leaves open: the page images were not checked, and the
  damaged-group readings were not tested. [L] **R**, 2026-11-01. NOTES.md itself (last
  adfgvx commit 31bf63e, 2026-10-28) was read by this chat's subagent on 2026-11-01.

**Letter comparison with our J1 `plain`** (single implementation, this chat, 2026-11-01).
Positions compared only where both texts have a letter:

| Unit | Length (ours / theirs) | Both known | Agree | Differences (position: ours / theirs) | Our edits |
|---|---|---|---|---|---|
| p0924#1 | 145 / 145 | 142 | 140 | 57: R/J (HPTM **R**OEL / **J**OEL); 76: E/A (ODESS**E** / ODESS**A**) | del1@38, ins1@35 |
| p110D | 88 / 88 | 84 | 84 | none | del1@27, ins1@28 |
| p190G | 67 / 67 | 63 | 62 | 51: D/S (MAKEN**D**EN / MAKEN**S**EN) | del1@37, ins1@39 |

Their texts:
- p0924: `AUFNAHMEFAEHIGXNIKOLAJEWXAUFWUNSCHXEZXKIEWXBESTIMMTXHPTMXJOELXVXOXFECHXODESSAX?ELCHESCHI?FEETWAXWEGENXEISENBAHNLAGEXNACHXNIKOLAJEWXZUGEHENHABENXX`
- p110D: `OHLXOPXZUDORT1A104660QEHOPDRAGTUNGEN1A11118GEHXOPXUND1A1?127GEHXOP?ERHALTENXOKM1A1116OO6`
- p190G: `BITTEXSOFORTXBE?CHEIDXOBXVERPINDUNGX?ISXARMEEXMAKENSENXEINWA?DFREIX`

**Why the texts differ.** Each difference is one letter. It could come from a square cell, a
transposition-edit placement, or the transcription; this chat did not try to tell which. It
does not change the verdict: these are the same readings.

### 1.3 0wwafa/adfgvx-1918 issue #1: p072A, p125B, p189B3 (and the three above)

- **Source.** "Proposed duplicate classifications, two identifications, and ADFGVX readings from
  the Childs log", AyushAg1002, 2026-10-28 13:48Z, open, no comments. [L] **R** by
  lit-adfgvx 2026-10-31 and re-read by this chat 2026-11-01.
- It calls itself "**provisional**" and "AI-assisted", "not yet checked against the Childs page
  images". It says each reading "was compared with matched random-key controls", but the
  controls are not posted.

Its status table, quoted:

| Entry | Their status | Their summary | Ours |
|---|---|---|---|
| p0924, part 2 | read | Nikolaev, the railway situation, and Captain Joel / Fech Odessa | same (see §1.2) |
| p110D | read | OHL orders Ia 104660, 11118, and 1?127 acknowledged by OKM | same (see §1.2) |
| p190G | read | *Bitte sofort Bescheid, ob Verbindung mit Armee Mackensen einwandfrei.* | same (see §1.2) |
| p072A | read, name uncertain | Liaison officer sent to Tiflis with OHL agreement | `MITEINVERST-…OHL?…WIRDRITTMXTELLNE-…VERBDGS…NACHXTIK-…ENTSANDO…HEERGRXKJEW`: overlapping (EINVERST[ÄNDNIS], RITTM[EISTER] TELLNE…, VERB[IN]D[UN]GS[OFFIZIER], "TIK-" = Tiflis?) |
| p125B | read in part | Radio reply requested concerning employment in the Ministry of Trade / demobilisation | `…DU-CHFUN-SP-UCH…HANDEL-M-NISTE…DEMO-I-MACHU…HAND-L-MINIS-ER`: overlapping |
| p189B3 | read in part | Men leaving for home on their own authority; OHL Ia | `DIESCHWIER-GKEITENXDASSMANNSCHAFTENEIGENMAECHTIGNACHHAUSEFAHRENWOLLEN…OHLXRMX1AXNRX11-01`: overlapping |

- **"Overlapping"** means the content agrees but no letters exist to compare. The bracketed
  expansions are this chat's gloss, made only to show the match. They are not a reading.
- The issue also claims **25 unsolved entries are second intercepts**, but the list is not
  posted. It also claims p155E, p192A, p101B2+p101B and p119A1, none of which is one of ours.

## 2. Screens run here against creilly's published log

[L]-adjacent bookkeeping, single implementation, 2026-11-01. These screens look for prior
readings. They are not mathematics, and they are not [C].

**Data.** creilly11235/adfgvx-1918 `data/records.json` @ e60da03, 688 entries. The default
branch is unchanged since e60da03 (2026-10-27). The only other branch, `claude/rebuild-story-data`
@ ec391d1, forks from c771d14, so it is older, and it changes no status of our units.

1. **Status.** All 25 creilly ids behind our 23 units are "Unsolved" at e60da03 and on the other
   branch. None has a plaintext, a key or a translation (`translations.json`: 592 entries, none
   of ours). The only credit on any of them is the 2017 one on p218C (§1.1).
2. **Plaintext overlap.** Each J1 `plain` was compared with every published creilly plaintext
   (status not Unsolved), counting shared letter 7-grams with separators removed.
   - The largest overlaps are all stock phrases: p213D/p137A4 share KRIEGSMINISTERIUM and
     MITTEILUNG; p189B3/p187_ share OHL RM IA NR GEH OP; p190G/p209A share BITTE SOFORT;
     p110D/p102D share GEH OP ERHALTEN; p141B.2/p09345 share ADMIRAL[STAB] SEEKRIEGSLEITUNG;
     p072B1/p212B share LEBENSMITTEL.
   - **No unit reproduces a published message.**
   - Context only: p102D (solved) is related traffic, an acknowledgement of "Ia Nr 11127 geh Op"
     to OHL, but it is a different text from p110D.
3. **Ciphertext duplicates.** For each unit's ciphertext (creilly transcription), we computed
   fixed-offset symbol agreement against all 688 entries at every offset with at least 40
   overlapping symbols.
   - The best agreement for any unit was 0.40–0.45 on 40–60 symbols. That is the chance level
     for the best of many short windows.
   - For comparison, the confirmed duplicate p155E/p139B agrees 88/104 (0.85).
   - **No unit is a fixed-offset duplicate intercept.**
   - Limitation: a copy with an insertion part-way through breaks a fixed offset. A gap-aware
     alignment, as Ayush used, was not run here.
4. **Norbert's 2017 hint** (#53) that a Childs p.186 message repeats the p.187 CHI message
   (p190A1/p190A, read in 2017). Checked: the published p190A plaintext ("RUSSISCHET UND POLN
   HEERESVERKEHR…") shares nothing with our p189B3. That hint is not about our unit.

## 3. Childs himself, and the 1918 record

[L] **R** by this chat's subagent, from the free scan (Google Drive PDF via Richard Bean's
Aegean Park index; sha256 `157e41a1…dc798ad06`, the same file lit-adfgvx used), 2026-11-01.

- **The book prints no plaintext of any intercepted message.** We found no decipherment,
  translation or "solved"/"read" mark anywhere in it:
  - Childs's paper (PDF 4–25) works 12 practice messages and gives keys only.
  - Appendix A (Konheim, PDF 26–57) is theory; it was spot-checked, not read page by page.
  - Appendix C (PDF 234–247) holds daily keys only.
  - On the 19 log pages holding our 23 units, nothing appears beyond the header and the
    ciphertext. The one exception is a reception note on PDF 190 B, "(Jammed by FL unable to
    read NKJ)".
- So no unit is "already solved by Childs" **on the evidence of this book**. Childs's 1919
  history and the archive files listed in `adfgvx.md` §2.5 were not read, so a 1918 decipherment
  cannot be excluded.
- **Appendix C does show which periods were broken in 1918.** It has keys for Sep 19–21, Oct 4–6,
  Oct 28–31, Nov 1–3, 4–6, 7–9, 10–12 (and Dec 1–3), 13–15 and 16–18 (and Dec 7–9). It notes
  that some keys were "received from M.I.1 B., British War Office".
  - Every unit's key except nov19, nov22 and nov28 is a period the Allies held in 1918.
  - Those periods were read then, but individual messages were not recorded as read. **Lasry et
    al.'s 618 of 668 includes an unknown subset of ours.**

**Headers as printed** (subagent transcription; the clear-text words may help the team):

| Unit | Header |
|---|---|
| p062A | `SSD, COS v ASO … 2250 (21.9) 3 TLE` |
| p071A | `COS, POT v NKJ … VON THO 1640 (5) 2 TEILE`, `1 TL CHI-220`, `2 TL CHI-186` / `RICHI-186` |
| p072B | `COS v NKJ … NR 298 FÜR COS HPTM GEMOLL (6) 2330 2 TLE` |
| p0924 | `OSM de LP … SSD BVG KOSPOLI (1/11) 1400 5 TEILE`, "(missed 20 groups)" |
| p110D | `LP v UKS … 1716 WH VON DRIGEND BIS KONSTANZA 2045`, RICHI-176 |
| p125B | `NKJ v LP … FUER UKS 1400 (4). OBERLEUTNANT VON SCHORLEMER OBERKOMMANDO M VERWALTUNGSSTAB.`, RICHI-252 |
| p139A | `COS v NKJ … DEUTSCHE DELEG KAUK MILITÄRKOMM GENERAL VON KRESS 0824 (5) 2 TLE` |
| p142A | `NKJ v LP … SSD FUER ASO 1940 3 TLE` |
| p153B | `LP v NKJ … 2100 (6) VON UKS 5 TLE`, with hand-corrected counts |
| p170D | `NKJ v LP … (RAT) SSD BLITZBLUECHER (9/11) 2245` |
| p189B | `NKJ v LP … FUER WAU 07.00 2 TLE`, with two smudged groups |
| p213D | `KOW v LP (05.55 p.m. November 20th) FUER RVA 22.00 (20/11)`, RICHI-116 (read by this chat) |
| p218A | `ZÖN v BSL … WORGAG DORT NR C 4 A 6688 1500 (11/22)` |
| p220B | `UKS v ZÖN … (missed beginning) 2 TLE` |

- **Transcription note: p190G.** On PDF 190 (Childs p.187) the entry is lettered **C**, not G:
  `C) NKJ v LP (16.09 p.m., November 13th) FUER UKS 12.45 (13/11) RICHI-134`. This chat viewed
  the page itself, 2026-11-01. creilly's "G" is an OCR misreading of the letter, and the header
  count 134 is against 135 symbols in the log. The unit id is creilly's and stays as it is.
- No source re-transcribed any of the 23 ciphertexts independently of creilly's typed log.
  Ayush and Bourdeau both used the typed log, and both say the images were not checked.

## 4. What was searched (2026-11-01)

| Source | Result | R/C |
|---|---|---|
| creilly11235/adfgvx-1918: all commits to HEAD e60da03 (2026-10-27), both branches, issues/PRs #9–#38, README, MESSAGES.md, records.json, translations.json, docs/story-data.js, messages/*.md for our ids | all 23 Unsolved; p218C credited to Norbert & Baertl 2017 (PR #23, 945d1b1); no new commit after e60da03 | R |
| 0wwafa/adfgvx-1918: HEAD 0839217 (2026-09-20), issue #1 (the only issue), fork lmchdev (no new commits); AyushAg1002's own repos (no ADFGVX repo) | §1.3 | R |
| dbourdeau/cyphersolver: issue #181 and comment; adfgvx.html (updated 2026-10-26); NOTES.md; HEAD 142b021 (2026-11-01) | §1.2. Our units otherwise absent; issue #181 is recorded but not marked solved | R (#181 by this chat; site and NOTES by subagent) |
| Schmeh: klausschmeh.net ADFGVX post 2026-09-21 and comments (Hongki Min, Krajcovic); scienceblogs.de 2014, 2015 and 2017 ADFGVX posts; the 2017 list page; the full 2017 comment thread | Only p218C (#17) is on the list; the 2017 thread reads it (§1.1). Norbert #24 and Baertl read p194A (part 1 of p194A.2's entry: "STELLV GEN KOM 9 A K BRESLAU … 4000 PAAR STIEFEL ZUNAECHST NACH ODERBERG"), not part 2. Hongki Min: no Childs ids, no usable text | R |
| Childs scan, PDF 4–57 and 234–247, plus the 19 log pages | §3 | R (subagent; p190 and p213 also by this chat) |
| Lasry thesis ch. 6 (via lit-adfgvx, `adfgvx.md` §2.1) | no per-message list | R, 2026-10-31 |
| Lasry, Niebel, Kopal, Wacker, Cryptologia 41(2) 2017 | paywalled; no per-message solutions online | C |
| Konheim (Appendix A of the Childs edition) | theory only | R (spot-checked) |
| arXiv API "ADFGVX"; IACR ePrint | 0 hits / nothing parseable | R |
| HistoCrypt 2025 / 2026 (NEALT 61, dspace.ut.ee) | **not reachable** (connection refused) | — |
| prinz (p.217), swarm-ai-research verification, The Neuron, Hacker News item 49763987 | p.217 only | R |
| GitHub repo search (adfgvx, updated since 2026-09-01): kajoty, Mqsirrel ×2, elder-plinius/V3R1T4S, joey-singer | none of our units | R |
| GitHub code search: EIGENMAECHTIG, MACKENSEN, NIKOLAJEW, REVAL, AUFNAHMEFAEHIG, MARINEVERTRETUNG, SEEKRIEGSLEITUNG, HERMANNSTADT, POTI | nothing beyond cyphersolver #181 | R |
| Web phrase searches: "Lage in Reval" + Kriegsministerium; "eigenmächtig nach Hause fahren"; "Verbindung mit Armee Mackensen"; Eisenbahnlage Nikolajew; Bahnlinien "in deutschen Betrieb genommen" Hermannstadt/Kronstadt; Seekriegsleitung / Marinevertretung; "kein Geld übermitteln" Kiew; "Pferde nach Poti" Batum; Braila Lebensmittel; Handelsminister ADFGVX | not found except at the two Ayush issues | snippets (C) |
| Reddit r/codes and r/cryptography, MysteryTwister, CrypTool forum | nothing found by web search; not fetched directly | C |

## 5. What could not be established

- **Lasry's private readings.** Lasry et al. (2017) read 618 of 668 cryptograms and published
  no per-entry list. Every one of our 23 units is read under one of Lasry's 14 published keys, so
  his 2017 search covered all of them. It is likely that some of the 16
  "new as far as searched" units were read by Lasry in 2017 and never published. **This cannot be
  settled from public sources.** Only Lasry can answer it, and contacting him is Aaron's call.
- **Ayush's unpublished sheets** and his list of 25 duplicates.
- **The 1918 record.** Childs's 1919 history, his 1935 report and the archive files (NARA
  RG 120, TNA HW 7/35, SHD Vincennes) were not read. A unit may have been read in 1918 without
  any public trace.
- HistoCrypt 2026 proceedings (unreachable), the Cryptologia full text (paywall), and the
  forums listed above (not fetched).
- Whether the 1–2 letter differences from cyphersolver #181 come from the square, the edits or
  the transcription. Not our role.
- Whether any reading is statistically real. Not our role, and not judged.
