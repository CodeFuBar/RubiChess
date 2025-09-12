# RubiChess vs Stockfish Evaluation Analysis Summary

## Overview
- Total positions compared: 135
- Flagged positions: 16
- Move agreement: 79.3%
- Mean absolute difference: 41.9 cp
- Max absolute difference: 309.0 cp

## Evaluation by Game Phase
| Phase | Count | Mean (cp) | Std Dev (cp) |
|-------|-------|-----------|-------------|
| endgame | 18.0 | 115.0 | 127.2 |
| opening | 117.0 | 30.6 | 43.6 |

## Flagged Positions
Positions with large evaluation differences (>100cp):

### Position 1 (ID: 15)
- **FEN**: `2kr3r/pppq1ppp/3p1n2/2b1p3/2B1P1b1/2NP1N2/PPP1QPPP/R1B1K2R w KQ - 0 1`
- **RubiChess**: 542 cp (h2h3)
- **Stockfish**: 424 cp (c4b3)
- **Difference**: +118 cp
- **Move Agreement**: No
- **Game Phase**: opening
- **Reason**: Large evaluation difference: +118cp

### Position 2 (ID: 22)
- **FEN**: `8/8/3k4/2ppp3/2PPP3/3K4/8/8 w - - 0 1`
- **RubiChess**: 783 cp (d4c5)
- **Stockfish**: 655 cp (d4c5)
- **Difference**: +128 cp
- **Move Agreement**: Yes
- **Game Phase**: endgame
- **Reason**: Large evaluation difference: +128cp

### Position 3 (ID: 23)
- **FEN**: `8/1p6/kP6/8/8/8/5K2/8 w - - 0 1`
- **RubiChess**: -701 cp (f2e1)
- **Stockfish**: -558 cp (f2e3)
- **Difference**: -143 cp
- **Move Agreement**: No
- **Game Phase**: endgame
- **Reason**: Large evaluation difference: -143cp

### Position 4 (ID: 26)
- **FEN**: `8/8/8/R7/8/3k4/5r2/4K3 w - - 0 1`
- **RubiChess**: 796 cp (e1f2)
- **Stockfish**: 510 cp (e1f2)
- **Difference**: +286 cp
- **Move Agreement**: Yes
- **Game Phase**: endgame
- **Reason**: Large evaluation difference: +286cp

### Position 5 (ID: 27)
- **FEN**: `8/8/8/8/5R2/3k4/5r2/4K3 w - - 0 1`
- **RubiChess**: 797 cp (f4f2)
- **Stockfish**: 506 cp (f4f2)
- **Difference**: +291 cp
- **Move Agreement**: Yes
- **Game Phase**: endgame
- **Reason**: Large evaluation difference: +291cp

### Position 6 (ID: 35)
- **FEN**: `8/8/8/8/8/3k1r2/8/4KR2 w - - 0 1`
- **RubiChess**: 775 cp (f1f3)
- **Stockfish**: 470 cp (f1f3)
- **Difference**: +305 cp
- **Move Agreement**: Yes
- **Game Phase**: endgame
- **Reason**: Large evaluation difference: +305cp

### Position 7 (ID: 36)
- **FEN**: `8/8/8/8/8/3k1n2/8/4KR2 w - - 0 1`
- **RubiChess**: 775 cp (f1f3)
- **Stockfish**: 540 cp (f1f3)
- **Difference**: +235 cp
- **Move Agreement**: Yes
- **Game Phase**: endgame
- **Reason**: Large evaluation difference: +235cp

### Position 8 (ID: 37)
- **FEN**: `8/8/8/8/8/3k1b2/8/4KR2 w - - 0 1`
- **RubiChess**: 775 cp (f1f3)
- **Stockfish**: 466 cp (f1f3)
- **Difference**: +309 cp
- **Move Agreement**: Yes
- **Game Phase**: endgame
- **Reason**: Large evaluation difference: +309cp

### Position 9 (ID: 39)
- **FEN**: `8/8/8/8/8/1K6/2P5/1k6 w - - 0 1`
- **RubiChess**: 967 cp (c2c4)
- **Stockfish**: 719 cp (c2c4)
- **Difference**: +248 cp
- **Move Agreement**: Yes
- **Game Phase**: endgame
- **Reason**: Large evaluation difference: +248cp

### Position 10 (ID: 60)
- **FEN**: `rn1qkbnr/pbp1p2p/5pp1/3p4/2pP4/P2Q4/1P1BPPPP/RN2KBNR b KQkq - 2 8`
- **RubiChess**: 488 cp (c4d3)
- **Stockfish**: 741 cp (c4d3)
- **Difference**: -253 cp
- **Move Agreement**: Yes
- **Game Phase**: opening
- **Reason**: Large evaluation difference: -253cp

### Position 11 (ID: 61)
- **FEN**: `rnb3nr/p2pbkp1/2p1p2p/qp1N1p2/PP6/2P2P1N/1BQPP1PP/R3KB1R w KQ - 2 11`
- **RubiChess**: 531 cp (b4a5)
- **Stockfish**: 708 cp (b4a5)
- **Difference**: -177 cp
- **Move Agreement**: Yes
- **Game Phase**: opening
- **Reason**: Large evaluation difference: -177cp

### Position 12 (ID: 98)
- **FEN**: `rnb1kbnr/p1pp1ppp/8/1p2p1q1/P5P1/3P3P/1PP1PP2/RNBQKBNR w KQkq - 1 5`
- **RubiChess**: 500 cp (c1g5)
- **Stockfish**: 681 cp (c1g5)
- **Difference**: -181 cp
- **Move Agreement**: Yes
- **Game Phase**: opening
- **Reason**: Large evaluation difference: -181cp

### Position 13 (ID: 103)
- **FEN**: `r2q2nr/ppp1pkbp/4bpp1/3P1P2/2Q5/3P4/PPP3PP/RNB1KBNR w KQ - 1 10`
- **RubiChess**: 548 cp (b1c3)
- **Stockfish**: 713 cp (f5e6)
- **Difference**: -165 cp
- **Move Agreement**: No
- **Game Phase**: opening
- **Reason**: Large evaluation difference: -165cp

### Position 14 (ID: 111)
- **FEN**: `rnbq1knr/1ppp4/p4p2/2b1p1Pp/3P4/2N4P/PPP1P1P1/R1BQKBNR w - - 1 10`
- **RubiChess**: 707 cp (d4c5)
- **Stockfish**: 575 cp (d4c5)
- **Difference**: +132 cp
- **Move Agreement**: Yes
- **Game Phase**: opening
- **Reason**: Large evaluation difference: +132cp

### Position 15 (ID: 115)
- **FEN**: `rnb1kbnr/p2p1p2/1p2p3/q5pp/1PP5/N2QB2N/P1P1PPPP/R3KB1R w KQkq - 0 8`
- **RubiChess**: 588 cp (b4a5)
- **Stockfish**: 706 cp (b4a5)
- **Difference**: -118 cp
- **Move Agreement**: Yes
- **Game Phase**: opening
- **Reason**: Large evaluation difference: -118cp

### Position 16 (ID: 129)
- **FEN**: `rnbqk1nr/6p1/Bpp1pp1p/p3P3/1b1p3P/5PP1/P1PP1K2/RNBQ2NR b kq - 0 10`
- **RubiChess**: 702 cp (b8a6)
- **Stockfish**: 515 cp (a8a6)
- **Difference**: +187 cp
- **Move Agreement**: No
- **Game Phase**: opening
- **Reason**: Large evaluation difference: +187cp

## Recommendations
Based on this comparison analysis, consider investigating:

1. **Large Evaluation Differences**: Focus on positions where engines disagree by >100cp
2. **Move Disagreements**: Positions where engines choose different moves may reveal tactical blind spots
3. **Systematic Biases**: Check if RubiChess consistently over/under-evaluates certain position types
4. **Phase-Specific Issues**: Analyze performance differences across opening/middlegame/endgame

## Next Steps
1. Manual review of flagged positions
2. Compare with other engines (when Stockfish issues are resolved)
3. Profile RubiChess evaluation function performance
4. Focus optimization efforts on identified weak areas
