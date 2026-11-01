# The open WWI ADFGVX messages (Childs log, Nov 1918)

**Final, 2026-11-01. Both strands are refereed:** strand R in Part E, strand J in Parts I–K
(I–J ACCEPT WITH REVISIONS, all revisions applied; K ACCEPT).
Lead: lead-adfgvx. Pre-registration: `findings/adfgvx-1918-prereg.md`. Referee's report:
`referee/adfgvx.md` (ref-adfgvx), Parts A–K, including what it could not check. Adversary:
`adversary/adfgvx*.md`. Novelty: `literature/adfgvx.md`, `literature/adfgvx-strandj-novelty.md`.

## Answer

1. **Schmeh's 2017 list of nine "open" messages is no longer the open set.** [L, 2026-10-31,
   `literature/adfgvx.md`, READ.]
   - The whole of Childs's Appendix B log (688 entries) was transcribed in October 2026, and 83
     entries are marked unsolved there.
   - Of Schmeh's nine, six now carry public solve or duplicate claims. Only p.73 (p076A), p.170
     (p173A) and p.198 (p201D) have none.
2. **We independently replicated the four outside claims about those nine (strand R).** None is
   ours. Verdicts use the pre-registered classes:

| | claim (claimant) | verdict | label |
|---|---|---|---|
| R1 | p.153 parts 5+6 (p156C3, p156C6) under a new 18-column key (creilly, 2026-10) | **PARTIAL** | decrypt [C], significance not established |
| R2 | p.176 GGDAA (p179B1) under Lasry's nov10 key + a 20-symbol gap (creilly, 2026-10) | **REPRODUCED**, for the letter reading only | decrypt [C]; null [S] |
| R3 | p.152 (p155E) is a second copy of solved p139B (0wwafa issue #1) | **REPRODUCED** as a duplicate relation | [S] |
| R4 | p.189 (p192A) is a damaged copy of solved p188_.2 (0wwafa issue #1) | **REPRODUCED** as a duplicate relation; the claimant's plaintext is not supported | [S] |

3. **About a quarter of the 83 "unsolved" log entries are copies of solved messages** (29 flagged,
   24 near-identical, on creilly's text) [S, comp duplicate screen, 2026-11-01; not yet
   second-implemented]. On the J0 scan units the screen flags 28 of 79, and the strand-J pool is
   49 (see Strand J).

4. **Strand J: for 22 of 49 'unsolved' log entries, the known period key is identified (with ≤ 2
   edits) and the decryption is reproduced [C].** That is what the pre-registered class
   READ-KNOWN-KEY means here. They pass both gates: independent reproduction, and an adversary
   that could not beat them with the same freedom. One more (p218A) is a detection the adversary
   beat.
   - "Read" overstates several of them, because much of the decryption is lost letters:
     p071A2 40% unknown, p102A 36%, p231B2 32%, p071A1 27%, p125B 26%, p220B 21%, p102C 21%. The
     per-unit unknown share is in the table below.
   - Seven of the 22 were already read or summarised publicly. For the other 15 we found no
     public reading. That is not a claim of a first solution (Lasry et al. 2017 read 618/668
     without a per-entry list).
   - The joint attacks (J2, J3) produced no reading.
   - J1 detected 5 of 12 positive controls on real text (Wilson 19–68%), below the
     pre-registered 50%. So it is formally underpowered, and its 26 negatives exclude nothing.

## What would make this wrong

- **Transcription.** Every R result rests on creilly's transcription @ e60da03. For p156C3,
  p156C6 and p179B1 it is symbol-identical to Schmeh's 2017 text. For p155E it differs at 2
  symbols and for p192A at 5; R3 survives on both, and R4 is weaker on Schmeh's. Neither is an
  independent reading of the scan. Our blind scan transcription now exists
  (`ciphertexts/adfgvx-1918-scan-transcription.*`), but strand R was not re-run on it.
- **R2's scorer.** The telegram-trained scorer (TEL) was chosen as primary after the
  literary-only scorer (LIT) had been seen to fail on R2. This was disclosed and counted as one of
  4 configurations.
  - The referee's independent scorer also separates the claim. It too was chosen knowing TEL
    worked, and this was disclosed.
  - Under LIT alone, R2 would be PARTIAL.
- **The scorer-freeze window.** check's scorer commit (50b772c, 22:30) is six minutes AFTER its
  first exploratory R scoring (22:24). That nothing changed in that window rests on a file mtime,
  which git does not record (referee E7).

## Evidence

### R1: p.153 under the 18-column key `16 7 13 4 15 8 17 3 1 12 14 2 5 9 10 18 11 6`

- **(i) decrypt.** Three implementations agree character for character: comp, check, and the
  referee's (the lead also re-derived part 5).
  - Part 5 reads `ANORDNUNGEN VOM 2TEN 11TEN NR 858 BEZIEHEN LASSEN SOWEIT NOCH NICHT
    GESCHEHEN` (66/66 letters).
  - **Part 6: of 54 letters, 37 decrypt directly and 2 only after a corrected log symbol. 15 are
    undetermined because they fall on lost symbols. Of those, 12 are conjectured by the claimant
    from context.** This is not "solved apart from three letters".
- **(ii) significance: NOT DONE.** This is the hard step.
  - The prereg requires a null with at least the claimant's search freedom. That means our own
    keyless solver, run on shuffled and real-decoy ciphertext.
  - check's solver does not find the claimed key on the real text (0/3), nor on planted controls
    (0/12). So its null maximum is not a null with the claimant's power, and the claim's margin
    over it (0.034/quad) certifies nothing.
  - The fixed-key rows (the claim beats 100 random keys, 100 shuffles and 100 real decoys under
    the claimed key by ≥ 0.24/quad) and unicity (≈ 48 letters at D = 3.4, against part 5's 66)
    are [H] context, not (ii).
  - The adversary independently found a higher-scoring alternative reading of part 5 alone,
    under the claimed transposition with a free square. So only the two parts jointly pin the
    square.
- What would settle it: a solver that recovers the claimed key on the real text, run with the
  same budget on same-length shuffles and planted controls.

### R2: p.176 GGDAA under nov10 with a gap

- The gap is marked in neither transcription: the header says 240 symbols and the log has 220.
  So the gap position is search freedom, and the null has it too.
- All letters that depend on the 20 gap symbols or on blank square cells are masked: 23 letters
  masked, 50 quadgrams scored.
- **(i)** All 100 letters outside the gap match the claimed reading: `… ARMEE ALPENKORPS RAUM
  PETERREVE VERBASZ … LINIE NAGYBESKIEREK VERSECZ VERSECZ VON SERBEN BESETZT`.
- **(ii)** check, TEL scorer, exhaustive over 21 lengths × 221 positions per key:
  - the claim is −1.064, the unique maximum over the nov10 grid;
  - best wrong key on p179B1: −1.570;
  - best of 970 solved-entry/wrong-key cases: −1.413.

  The lead re-ran this from a clean export and got identical numbers. The referee's own scorer
  gives claim −4.960 against −5.357 and −5.171 (201 grids).
- **Not reproduced:** the gap position "160". Positions from about 152 to 162 score within
  0.009/quad of each other, so say "about 152–162". The digits `217`, `216` and `9` are not
  reproduced either: they depend on blank-cell fills from a 2017 blog comment.

### R3, R4: duplicates

- R3: 88 of 102 readable symbols of p155E equal p139B at offset 210. Chance is 17.0 ± 3.8, and
  the null maximum over all other solved entries is 37.
- R4: 52 of 79 symbols equal p188_.2 at offset 0. The null maximum is 29. A gap-aware alignment
  gives 63 equal against 16 different, which is the claimant's count.
- These are relations between ciphertexts only. R4's claimed plaintext "Gestellung Auto
  unmöglich" rests on one letter that disagrees with p188_.2's own log, and is **not supported**.
- R3 adds nothing new to read, because p139B is already fully read.


## Strand J: the unread pool (results, 2026-11-01; refereed, Parts I–J)

Pre-registration: `findings/adfgvx-1918-prereg.md`, strand J. It was accepted at 8a1bcf8, with
clarifications C1–C2, amendment C3 and the referee Part H conditions at 91996a0. Every step was
committed before the next one ran, so the order can be checked from git (comp-adfgvx J0 d2c2dc6 →
J3 3d8173d → creilly re-run b9b5666).
- Primary transcription: our blind scan transcription.
- Pool: 49 entries that creilly @ e60da03 marks Unsolved, of the 79 J0 scan units (83 entries,
  p220C dropped, p0924 split, four joins) less 28 flagged as copies of solved messages (12
  plant-side and 16 train-side controls; `results/adfgvx-duplicates-J0.md`) and 2 under 60
  letters: 79 - 28 - 2 = 49. (Corrected 2026-11-01 after merge; it said '21 near-copies', which
  does not add up.)
- **False-detection bound (revised after referee I1).** The prereg intended each family to be
  below 1/60, giving < 5% for the strand. That bound needs every null draw to be exchangeable with
  the target, and the two halves of the null are not.
  - Half (a), the target's own text shuffled, scores far above half (b), plant-side text with
    creilly's lower lost rate (e.g. J1 p071A2 means −3.53 vs −4.09; J3 −3.51 vs −3.87).
  - Only half (a) supports a bound: **J1 ≤ 49/1471 = 3.3%, J2 ≤ 5/151 = 3.3%, J3 ≤ 1/31 = 3.2%.**
  - **J1 ≤ 3.3%** (half (a), and a mask-matched null, referee Part K: 1,470 draws per detection,
    0 reaching S for all 23; tightest p071A2, S −3.383 vs masked max −3.415) [S]. **There is no bound for J2/J3 on damaged groups, so none for strand
    J as a whole.**
  - **For J2 and J3 on damaged groups, half (a) is NOT valid** (adversary J3, see below). So the
    J2/J3 bounds do not hold there.
  - The thresholds themselves are unchanged (the max over both halves), and so are the
    detections.

### Answer

1. **J1, known period key + ≤ 2 edits: 23 of 49 entries are detected, and 22 pass both reading
   gates (READ-KNOWN-KEY).**
   - **Gate (i):** an independent implementation reproduced all 23 decryptions character for
     character (check-adfgvx-j1, 81dac12; the lead re-ran it) [C].
   - **Gate (ii):** the adversary, given the same freedom, beat one of them: **p218A**, which
     stays a detection and is not a reading (adv-adfgvx, `adversary/adfgvx-j1.md`, f8f616d).
     - **The rule used:** "a wrong key" means ANY of the other 21 keys in the key file,
       including keys with blank cells.
     - p218A is beaten by nov13_20 (12 blank cells, −3.537) and by childs_jul18 (−3.518). Under a
       blank-free-only rule it would survive (best blank-free key nov25, −4.048). We use the
       wider rule.
   - **Random keys on the real ciphertext (CLAUDE.md test 3).** For each of the other 22, the
     adversary ran 2,600 random keys per unit: uniform; with Lasry blank patterns; the claimed
     square with a random transposition; and the claimed transposition with a random square.
     None reached S [S].
     - The adversary's search over the 21 other keys was exhaustive at cap 2. It is one
       implementation (e2.c), cross-checked against comp on all 64 (target, candidate-key) pairs,
       so it is not [C] as a search.
     - p062A, the thinnest margin, survives at caps 1, 2 and 3 (+0.024 / +0.011 / +0.057 over
       nov13_20, with 0 random keys reaching S). It is not a reading at cap 0. The claimed key
       gains more per extra edit than any wrong key (adversary, `adversary/adfgvx-j1.md`).
     - None of the readings is a near-copy of a solved plaintext. The longest shared substring
       is 18 letters (`XKRIEGSMINISTERIUM`).
   - **What READ-KNOWN-KEY means here:** the key is identified at the stated level, and the
     decryption is reproduced [C]. It does not say the plaintext is legible.
     - Legibility is not ranked by the margin over the best wrong key. That margin is set by
       blank-heavy keys (nov13_20 is the best wrong key on 18 of 23 units), so it measures
       distance from the −3.58 unknown charge, not readability. (Referee I2; for example, p072B1
       is 2% unknown with a large S−threshold margin, yet has a small wrong-key margin.)
     - Readability is shown by the unknown share in the table and by the plaintext excerpts. The
       lead's judgement that p189B3, p213D, p0924#1, p141B.2, p190G, p153B4+p153B, p139A2, p072A,
       p110D and p072B1 "read as German" is the lead's reading [H], not a measured property.
   - The statistic charges a trigram with an unknown letter ln(1/36) = −3.58. So readings scoring
     between about −3.45 and −3.30 beat only wrong readings that say nothing (adversary).
   - **J1 negatives: the measured detection rate on real text is 5/12 (Wilson 19–68%).** That is
     below the pre-registered 50%, so J1 is formally UNDERPOWERED. The '~91%' figure elsewhere is
     the cap's coverage of the damage model, not power. Post hoc and descriptive only: 6 of the 7
     misses are fragments of their solved twin (twin more than 10% longer): fragments 0/6, the
     other plant-side controls 5/6 (results/adfgvx-J.md). So every J1 NEGATIVE (26 entries) reads as
     "uninformative" or "not detected at low power". None is an exclusion.
2. **Novelty.** Of the 23 detections (lit-adfgvx-j, PR #25):
   - **already read publicly (4):** p218C (Norbert/Baertl, 2017), p0924#1, p110D and p190G
     (cyphersolver #181, 28 Oct 2026). These are replications.
   - **content summarised publicly, without letters (3):** p072A, p125B, p189B3 (0wwafa #1).
   - **no public reading found (16).** This is NOT a claim of a first solution. Lasry et al. 2017
     read 618 of 668 messages under these keys without publishing a per-entry list.
3. **Why these were "unsolved".**
   - 6 of the 23 detections need our scan transcription: p072B1, p102C, p139A2, p153B4+p153B,
     p189B3, p231B2. In each, creilly's transcription is 3–50 symbols short.
   - The other 17 are also detected on creilly's text, because ≤ 2 edits repair it. For them, the
     period key with a small edit search had apparently just not been applied, or not published.
4. **J2, known square + unknown transposition, joint: no reading.**
   - Four of five tests are negative.
   - The one exceedance (the nov07/nov10 group under the nov10 square, +0.0032, width 22) decrypts
     to no German. It is reported as a detection with no reading.
   - **The J2 family bound does not hold for damaged groups** (see J3). This exceedance shares
     J3's null construction and was not tested against a mask-matched null.
5. **J3, keyless joint: one LEAD, no reading.** The nov07 group (850 letters) cleared its 60-draw
   null by +0.0042 at width 22. Its decryption was reproduced (check-adfgvx-j3) and is letter
   salad. A J3 detection is a lead by rule, and stays one.
   - **The J3 family bound does not hold for damaged groups.** The shuffled half of the null is
     biased low when lost symbols come in bursts, and the plant-side half carries no lost
     symbols, so the threshold came from the shuffles alone.
   - **The exceedance is reproduced by lost-symbol masking alone, with no key** [S]
     (`adversary/adfgvx-j3.md`, adv-adfgvx 39a7a19 / dev a1a7590; the adversary reproduces S
     exactly).
     - Real ciphertext beats its own shuffles by about 0.009 under ANY transposition once the
       square is free. Shuffling destroys the column structure and the burst pattern of the lost
       symbols (206 of 1056 lost, in bursts of 77, 67 and 27). That offset exceeds the +0.0042
       margin.
     - A matched null, made of real ciphertexts under other keys with each member's own
       lost-symbol mask imposed, puts the group at about the 87th percentile.
     - The adversary's own joint search does not separate the real group from shuffles or from
       matched draws.
   - No re-draw is made, because no reading is at stake (dev's ruling).
6. **Not tested:** RIZI/CHI groups under any non-period key except the one declared CHI trial;
   transposition widths ≥ 23; the all-14-keys J1 pass (F7); p071A2 as RICHI (amendment C3); a
   **mask-matched null for J2/J3**.

### J1 detections: margins and status

The margin over the best wrong key is S minus the best score the adversary found under any of the
other 21 keys (first figure) or the other 13 period keys (second figure), with the same ≤ 2 edits.
"Unknown letters" is the share of `-` or `?` in the claimed plaintext. "On creilly text" says
whether the detection survives the robustness re-run. Rows are sorted by the wrong-key margin. That is NOT an order of legibility (referee I2); see the unknown-letters column.

| unit | key | edits | S | threshold | margin over best wrong key (any / period) | unknown letters | on creilly text | prior public reading | plaintext (first 50) |
|---|---|---|---|---|---|---|---|---|---|
| p189B3 | nov13_16 | del1@92,ins1@93 | -2.157 | -3.289 | +1.304 / +1.338 | 2% | NO (scan only) | summarised in part (0wwafa #1) | `DIESCHWIER-GKEITENXDASSMANNSCHAFTENEIGENMAECHTIGNA` |
| p213D | nov19 | del1@6,ins1@5 | -2.324 | -3.414 | +1.058 / +1.178 | 2% | yes | none found | `BITTEU-MITTEILUNGXWIELAGEINXREVALXKRIEGSMINISTERIU` |
| p0924#1 | nov01 | del1@38,ins1@35 | -2.564 | -3.769 | +0.942 / +0.942 | 2% | yes | KNOWN (cyphersolver #181) | `AUFNAHMEFAEHIGXNIKOLAJEWXAUFWUNSCHXEZXKIEWXBEST-MM` |
| p141B.2 | nov04 | ins1@195,ins1@285 | -2.545 | -3.777 | +0.942 / +0.945 | 6% | yes | none found | `SEEK--EGSLEITUNG-ROSSESXHZYUXXADMIRALBERLINXXPACHC` |
| p190G | nov13_20 | del1@37,ins1@39 | -2.486 | -3.030 | +0.912 / +1.001 | 4% | yes | KNOWN (cyphersolver #181) | `BITTEXSOFORTXBE-CHEIDXOBXVERPINDUNGXMISXARMEEXMAKE` |
| p153B4+p153B | nov04 | del1@72,ins1@74 | -2.536 | -3.638 | +0.879 / +0.879 | 10% | NO (scan only) | none found | `SIN-NACHXRON-TADT-XH-RMANNSTA-TVORAUS-ESCHICKTX-AH` |
| p139A2 | nov04 | del1@79,ins1@81 | -2.603 | -3.211 | +0.725 / +0.758 | 4% | NO (scan only) | none found | `KEING-LDUEBERMITTELNXHEERESGRXKREWX1CXHR-8536X` |
| p072A | oct04 | del1@78,ins1@77 | -2.724 | -3.780 | +0.663 / +0.822 | 5% | yes | summarised (0wwafa #1) | `MITEINVERST-EWDNISXOXHXLXWIRDRITTMXTELLNE-XTELLN1R` |
| p194A.2 | nov13_16 | del5@55,ins5@25 | -2.759 | -3.306 | +0.660 / +0.660 | 14% | yes | none found | `WNTERVORXELDUNGMNTST-R-EBBEKLE-DFGAUFA-RUFBERE-TST` |
| p110D | nov01 | del1@27,ins1@28 | -2.745 | -3.570 | +0.643 / +0.712 | 3% | yes | KNOWN (cyphersolver #181) | `OHLXOPXZUDORT1A104660QEHOPDRAGTUNGEN1A11118GEHXOPX` |
| p102C | nov01 | del5@125,ins5@115 | -2.921 | -3.447 | +0.455 / +0.519 | 21% | NO (scan only) | none found | `OXHX-9OPXDIEW--POSTXFU---AXOXKX---XNACHGA---SONKOM` |
| p102A | nov01 | del1@27,ins1@133 | -3.120 | -3.332 | +0.309 / +0.309 | 36% | yes | none found | `--BITTE-V--SCHLA-FU--V-RKE-R--EITEN-WI--E-RIN-B--N` |
| p218C | nov22 | ins5@25,ins5@215 | -3.164 | -3.750 | +0.296 / +0.387 | 16% | yes | KNOWN (Norbert/Baertl 2017) | `ABSXMI-I5XNA6M-LD-X-4NXS4-XN-R-DAKER-SC-X-RINGTENT` |
| p072B1 | oct04 | del1@37,ins1@303 | -3.180 | -4.015 | +0.279 / +0.381 | 2% | NO (scan only) | none found | `AIBRAILA4X1RXMITDXVIOLEDTAX10000EIHRHAND--9NALENX3` |
| p125B | nov04 | del1@91,ins1@88 | -3.239 | -3.486 | +0.230 / +0.230 | 26% | yes | summarised in part (0wwafa #1) | `T-BI-TERDE-KA-TFOR-DU-CHFUN-SP-UCHO-SI-ZU-BE-CH-E-` |
| p231B2 | nov28 | del5@195,ins5@255 | -3.315 | -3.510 | +0.177 / +0.212 | 32% | NO (scan only) | none found | `A-ST--CKEHAN--FULDAD--OBILGE---HTDIB--CHANLG--UJDE` |
| p142A2+p142A | nov04 | del5@70,ins5@75 | -3.277 | -3.744 | +0.172 / +0.208 | 5% | yes | none found | `XAX-RX11120XGEHOPXCUJOMAREMOX36117X59000X13814X398` |
| p220B | nov22 | del1@5,ins1@15 | -3.330 | -3.506 | +0.106 / +0.146 | 21% | yes | none found | `YBENDM-L-F7ALPXKORP-AHP--EREZU-9RABGEROLL-QSY0XIDU` |
| p071A1 | oct04 | del1@86,ins1@97 | -3.372 | -3.492 | +0.101 / +0.163 | 27% | yes | none found | `G-NE--L-KR-SSXT--L-LXX-1TS--U-6NR-159-----9XBZTR--` |
| p071A2 | oct04 | del1@49,ins1@45 | -3.383 | -3.423 | +0.094 / +0.094 | 40% | yes | none found | `--DARTILLER--T7QI-JO-F--DO-RH-I----GD-RSEI-G--A--E` |
| p170D | nov07 | del1@116,ins1@97 | -3.369 | -3.432 | +0.088 / +0.088 | 9% | yes | none found | `H-TYGLIMMER2AFEKODESELXDFSDEILO0HLAWIRDN0--RZ2211-` |
| p062A | sep19 | ins1@131,del5@200 | -3.452 | -3.628 | +0.011 / +0.011 | 7% | yes | none found | `6X--FFQ-74XHG6AM11X9XAUF9AMPF-RXVUR-A4VA-NAX5XBATT` |
| p218A | nov22 | ins1@158,ins1@186 | -3.683 | -3.873 | -0.165 / -0.147 | 10% | yes | none found | `DPVAESENDUNGO0ERXYAXAR-EVDRI-JXBE-H-TSG-2NXJ-J117P` |

### What would make strand J wrong

- **The scan transcription.** One transcriber with a second reader channel; it is not [C]. Six
  detections depend on it.
- **The key list.** The keys are taken as published (creilly's copy of Lasry et al.), not
  re-derived. A wrong key cell would garble readings, but could not create them.
- **The scorer.** A trigram model on about 30k characters of period text. Each detection depends
  on it; how sensitive each one is was not measured. The lead expects detections with a high
  unknown share to be the most sensitive [H].
- **The edit rule.** jattack silently drops some edit combinations (adversary). This applies to
  the claims and the null alike.

## What we could not establish

- R1 (ii): see above. Neither our solver, the adversary's nor the referee's reaches the claimed
  key.
- R2: the "four separate groups of five" gap variant that the claimant searched (194,756
  placements) was not run.
- Strand J: see 'Not tested' in the strand J section. Also not established: whether Lasry et al. 2017 already hold readings of the 15 units with no public reading. Asking them is Aaron's call.

## Errata after merge (2026-11-01, dev, from the labs writer's review)

These sit in files whose owners' chats are closed (`adversary/`, `referee/`, `verify/` are role-owned
and not edited here), so they are recorded in this finding instead. None changes a reading or a
bound.

- `adversary/adfgvx-j1.md` line 9 labels the wrong-key search [C]. It is one implementation,
  cross-checked against comp's S on 64 pairs (referee I4; Strand J above). Read it as [S].
- Referee Part K says the masked-null mean is above the shuffle mean for four units. Recomputed
  from `referee/adfgvx-r/j1mask.jsonl.gz` and `results/adfgvx-J1-nulls-a.jsonl.gz` it is five:
  p220B also, −3.7165 vs −3.7185 (+0.002). The conclusion (0 of 1,470 masked draws reach S for
  all 23) is unaffected.
- **Blindness disclosure for check-adfgvx-j1.** Before writing `verify/adfgvx/J1-repro.py`, that
  chat printed the first 30 characters of comp's p062A plaintext in an inspection command
  (11:30:36Z). Its script computes before reading `plain`, and the decryption is deterministic,
  but `verify/adfgvx/J1-REPRO.md` does not disclose this. "Reproduced blind" means: blind except
  that one 30-character view of one unit's output.
- The target was chosen by `dev` from Aaron's request for "the WW1-era codes", not named by Aaron.
