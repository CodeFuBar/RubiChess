# Phase 2: Evaluation Component Analysis Report

**Generated:** 2025-11-24 21:43:28

---

## Executive Summary

- **Positions Analyzed:** 3
- **Average Evaluation Difference:** +794.7cp
- **Largest Discrepancy:** 98 (1343cp)

## Detailed Position Analysis

### Position 60

**FEN:** `r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/3PbN2/PPP2PPP/RNBQ1RK1 w kq - 1 6`

#### Evaluation Summary

| Engine | Evaluation |
|--------|------------|
| RubiChess | +960 cp |
| Stockfish | +197 cp |
| **Difference** | **+763 cp** |

#### RubiChess Component Breakdown

| Component | Middlegame | Endgame | Average |
|-----------|------------|---------|----------|
| Material | +960 | +960 | +960.0 |
| Minors | +0 | +0 | +0.0 |
| Rooks | +0 | +0 | +0.0 |
| Pawns | +0 | +0 | +0.0 |
| Passers | +0 | +0 | +0.0 |
| Mobility | +0 | +0 | +0.0 |
| **Threats** | **+0** | **+0** | **+0.0** |
| King Attacks | +0 | +0 | +0.0 |
| Complexity | +0 | +0 | +0.0 |
| Tempo | +0 | +0 | +0.0 |

#### Stockfish Component Breakdown

| Component | Value (pawns) | Value (cp) |
|-----------|---------------|------------|
| Material (PSQT) | -0.08 | -8 |
| Positional (Layers) | +1.59 | +159 |
| NNUE Eval | +1.51 | +151 |
| Final Eval | +1.97 | +197 |

#### Key Discrepancies

- **Material Psqt**: +968.0cp
- **Mobility Positional**: -159.0cp

#### Recommendations

CRITICAL DISCREPANCY: 763cp difference
Priority: Immediate parameter review needed
MOBILITY: -159.0cp difference vs Stockfish
  -> Review eMobilitybonus array values
TENDENCY: RubiChess overvalues this position type
  -> Consider reducing relevant bonuses

---

### Position 98

**FEN:** `8/8/2k5/5p2/6p1/2K5/3P4/8 b - - 1 1`

#### Evaluation Summary

| Engine | Evaluation |
|--------|------------|
| RubiChess | +837 cp |
| Stockfish | -506 cp |
| **Difference** | **+1343 cp** |

#### RubiChess Component Breakdown

| Component | Middlegame | Endgame | Average |
|-----------|------------|---------|----------|
| Material | +837 | +837 | +837.0 |
| Minors | +0 | +0 | +0.0 |
| Rooks | +0 | +0 | +0.0 |
| Pawns | +0 | +0 | +0.0 |
| Passers | +0 | +0 | +0.0 |
| Mobility | +0 | +0 | +0.0 |
| **Threats** | **+0** | **+0** | **+0.0** |
| King Attacks | +0 | +0 | +0.0 |
| Complexity | +0 | +0 | +0.0 |
| Tempo | +0 | +0 | +0.0 |

#### Stockfish Component Breakdown

| Component | Value (pawns) | Value (cp) |
|-----------|---------------|------------|
| Material (PSQT) | +0.25 | +25 |
| Positional (Layers) | +5.19 | +519 |
| NNUE Eval | -5.45 | -545 |
| Final Eval | -5.06 | -506 |

#### Key Discrepancies

- **Material Psqt**: +812.0cp
- **Mobility Positional**: -519.0cp

#### Recommendations

CRITICAL DISCREPANCY: 1343cp difference
Priority: Immediate parameter review needed
MOBILITY: -519.0cp difference vs Stockfish
  -> Review eMobilitybonus array values
TENDENCY: RubiChess overvalues this position type
  -> Consider reducing relevant bonuses

---

### Position 103

**FEN:** `8/8/1p1k4/3p4/3P4/1P6/4K3/8 b - - 1 1`

#### Evaluation Summary

| Engine | Evaluation |
|--------|------------|
| RubiChess | +242 cp |
| Stockfish | -36 cp |
| **Difference** | **+278 cp** |

#### RubiChess Component Breakdown

| Component | Middlegame | Endgame | Average |
|-----------|------------|---------|----------|
| Material | +242 | +242 | +242.0 |
| Minors | +0 | +0 | +0.0 |
| Rooks | +0 | +0 | +0.0 |
| Pawns | +0 | +0 | +0.0 |
| Passers | +0 | +0 | +0.0 |
| Mobility | +0 | +0 | +0.0 |
| **Threats** | **+0** | **+0** | **+0.0** |
| King Attacks | +0 | +0 | +0.0 |
| Complexity | +0 | +0 | +0.0 |
| Tempo | +0 | +0 | +0.0 |

#### Stockfish Component Breakdown

| Component | Value (pawns) | Value (cp) |
|-----------|---------------|------------|
| Material (PSQT) | +0.09 | +9 |
| Positional (Layers) | +0.26 | +26 |
| NNUE Eval | -0.35 | -35 |
| Final Eval | -0.36 | -36 |

#### Key Discrepancies

- **Material Psqt**: +233.0cp
- **Mobility Positional**: -26.0cp

#### Recommendations

CRITICAL DISCREPANCY: 278cp difference
Priority: Immediate parameter review needed
TENDENCY: RubiChess overvalues this position type
  -> Consider reducing relevant bonuses

---

## Overall Recommendations

1.   -> Consider reducing relevant bonuses
2.   -> Review eMobilitybonus array values
3. CRITICAL DISCREPANCY: 1343cp difference
4. CRITICAL DISCREPANCY: 278cp difference
5. CRITICAL DISCREPANCY: 763cp difference
6. MOBILITY: -159.0cp difference vs Stockfish
7. MOBILITY: -519.0cp difference vs Stockfish
8. Priority: Immediate parameter review needed
9. TENDENCY: RubiChess overvalues this position type

---

## Next Steps

1. Review component discrepancies
2. Implement parameter adjustments
3. Re-test positions for improvement
4. Validate no regressions on Phase 1 positions
