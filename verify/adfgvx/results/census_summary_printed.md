**ALL solved entries with plaintext+key**: 595 messages, 128380 sent symbols
- messages with 0 events: 451 (75.8%)
- events (E1,E2,E3,E5,E6 counted; E4 separate): 250 total = 0.420 per message = 0.195 per 100 sent symbols
- distribution of events per message: 0:451, 1:90, 2:28, 3:13, 4:7, 5:2, 6+:4
- by type (events / symbols affected): E1 49/206, E2 110/437, E3 45/300, E5 43/43, E6 3/3
- unreadable symbols '-'/'?' in the log (E4): 895 = 0.696 per 100 logged symbols

**wildcard fraction < 10% of sent symbols**: 569 messages, 122878 sent symbols
- messages with 0 events: 436 (76.6%)
- events (E1,E2,E3,E5,E6 counted; E4 separate): 231 total = 0.406 per message = 0.188 per 100 sent symbols
- distribution of events per message: 0:436, 1:84, 2:26, 3:10, 4:7, 5:2, 6+:4
- by type (events / symbols affected): E1 45/198, E2 103/430, E3 38/240, E5 42/42, E6 3/3
- unreadable symbols '-'/'?' in the log (E4): 583 = 0.474 per 100 logged symbols

**method = as transcribed (no repair)**: 465 messages, 98626 sent symbols
- messages with 0 events: 449 (96.6%)
- events (E1,E2,E3,E5,E6 counted; E4 separate): 16 total = 0.034 per message = 0.016 per 100 sent symbols
- distribution of events per message: 0:449, 1:16, 2:0, 3:0, 4:0, 5:0, 6+:0
- by type (events / symbols affected): E1 0/0, E2 16/16, E3 0/0, E5 0/0, E6 0/0
- unreadable symbols '-'/'?' in the log (E4): 602 = 0.610 per 100 logged symbols

**all other methods**: 130 messages, 29754 sent symbols
- messages with 0 events: 2 (1.5%)
- events (E1,E2,E3,E5,E6 counted; E4 separate): 234 total = 1.800 per message = 0.786 per 100 sent symbols
- distribution of events per message: 0:2, 1:74, 2:28, 3:13, 4:7, 5:2, 6+:4
- by type (events / symbols affected): E1 49/206, E2 94/421, E3 45/300, E5 43/43, E6 3/3
- unreadable symbols '-'/'?' in the log (E4): 293 = 0.981 per 100 logged symbols

**method = length repaired**: 79 messages, 18336 sent symbols
- messages with 0 events: 0 (0.0%)
- events (E1,E2,E3,E5,E6 counted; E4 separate): 103 total = 1.304 per message = 0.562 per 100 sent symbols
- distribution of events per message: 0:0, 1:61, 2:12, 3:6, 4:0, 5:0, 6+:0
- by type (events / symbols affected): E1 24/46, E2 55/65, E3 20/105, E5 2/2, E6 2/2
- unreadable symbols '-'/'?' in the log (E4): 133 = 0.727 per 100 logged symbols

| key | n msgs | sent symbols | events/msg | events/100 sym |
|---|---|---|---|---|
| chi_2017_comments | 2 | 354 | 0.00 | 0.00 |
| dec09_history | 1 | 170 | 0.00 | 0.00 |
| nov01 | 97 | 22256 | 0.27 | 0.12 |
| nov04 | 101 | 22746 | 0.42 | 0.18 |
| nov07 | 89 | 17314 | 0.73 | 0.38 |
| nov10 | 46 | 8142 | 0.61 | 0.34 |
| nov13_16 | 50 | 9862 | 0.26 | 0.13 |
| nov13_20 | 11 | 2180 | 0.82 | 0.41 |
| nov16 | 35 | 7956 | 0.09 | 0.04 |
| nov19 | 11 | 2572 | 0.00 | 0.00 |
| nov22 | 24 | 5382 | 0.38 | 0.17 |
| nov25 | 33 | 8352 | 0.27 | 0.11 |
| nov28 | 28 | 6434 | 0.36 | 0.16 |
| oct04 | 21 | 4588 | 0.86 | 0.39 |
| oct28 | 32 | 7406 | 0.28 | 0.12 |
| sep19 | 14 | 2666 | 0.64 | 0.34 |

sent length 0-100: n=42, events/100sym 0.32, any-event fraction 0.12

sent length 100-200: n=220, events/100sym 0.22, any-event fraction 0.21

sent length 200-300: n=242, events/100sym 0.20, any-event fraction 0.28

sent length 300-1000000: n=91, events/100sym 0.14, any-event fraction 0.27

worst by alignment cost:
- p149C1 (nov04) sent 176 log 367 cost 13.65 cipher-space [['E5', 1], ['E1', 1], ['E2', 192], ['E5', 1]]
- p183D1 (nov10) sent 196 log 197 cost 8.05 cipher-space [['E5', 1], ['E5', 1], ['E5', 1], ['E5', 1], ['E5', 1], ['E5', 1], ['E5', 1], ['E2', 1]]
- p073A1 (oct04) sent 322 log 332 cost 7.50 cipher-space [['E5', 1], ['E5', 1], ['E5', 1], ['E5', 1], ['E3', 5], ['E5', 1], ['E3', 5]]
- p162A (nov07) sent 272 log 272 cost 7.00 cipher-space [['E3', 5], ['E3', 5], ['E5', 1], ['E2', 5], ['E1', 5], ['E5', 1]]
- p160A3 (nov07) sent 218 log 211 cost 6.35 cipher-space [['E5', 1], ['E1', 5], ['E5', 1], ['E5', 1], ['E1', 2], ['E5', 1]]
- p178C3 (nov10) sent 222 log 217 cost 5.85 cipher-space [['E2', 3], ['E1', 3], ['E1', 5], ['E2', 3], ['E1', 3]]
- p170A (nov07) sent 204 log 200 cost 5.20 cipher-space [['E5', 1], ['E5', 1], ['E5', 1], ['E5', 1], ['E1', 4]]
- p163B (nov07) sent 282 log 257 cost 5.15 cipher-space [['E3', 5], ['E2', 9], ['E1', 29]]
- p165B1 (nov07) sent 182 log 161 cost 5.05 cipher-space [['E1', 1], ['E1', 10], ['E1', 10], ['E5', 1]]
- p186B (nov10) sent 74 log 60 cost 4.80 cipher-space [['E1', 1], ['E2', 1], ['E5', 1], ['E1', 14]]
- p168A5 (nov07) sent 500 log 485 cost 4.75 cipher-space [['E3', 5], ['E5', 1], ['E3', 5], ['E3', 5]]
- p193_ (nov13_20) sent 176 log 175 cost 4.75 cipher-space [['E2', 7], ['E1', 8], ['E5', 1], ['E5', 1]]
