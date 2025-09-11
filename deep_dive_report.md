# Deep Dive Analysis: Positions 135-142
## Critical Evaluation Failure Investigation

### Executive Summary

Deep dive analysis of the 8 worst-performing positions from large-scale weakness testing.

**Positions Analyzed:** 135, 136, 137, 138, 139, 140, 141, 142
**Analysis Completed:** 8/8 positions

---

## Summary Table

| Position | Baseline Move/Eval | Extended Move/Eval | Reference Move/Eval | Critical Issues |
|----------|-------------------|-------------------|-------------------|-----------------|
| 135 | d3d4 (-815cp) | d3d4 (-797cp) | d3e4 (-448cp) | MOVE_DIFFERS_FROM_REFERENCE, LARGE_EVAL_DIFF_VS_REFERENCE |
| 136 | h1h3 (+811cp) | h1h3 (+819cp) | h1h4 (+472cp) | MOVE_DIFFERS_FROM_REFERENCE, LARGE_EVAL_DIFF_VS_REFERENCE |
| 137 | h1h2 (+805cp) | h1h2 (+818cp) | h1h3 (+728cp) | MOVE_DIFFERS_FROM_REFERENCE |
| 138 | d3c3 (-825cp) | d3e3 (-823cp) | d3c3 (-479cp) | MOVE_CHANGE_WITH_DEPTH, LARGE_EVAL_DIFF_VS_REFERENCE |
| 139 | d3e3 (-829cp) | d3e3 (-825cp) | d3e4 (-473cp) | MOVE_DIFFERS_FROM_REFERENCE, LARGE_EVAL_DIFF_VS_REFERENCE |
| 140 | c1d2 (+811cp) | c1d2 (+812cp) | c1d2 (+455cp) | LARGE_EVAL_DIFF_VS_REFERENCE |
| 141 | h4h3 (+810cp) | h4h3 (+822cp) | d1e2 (+531cp) | MOVE_DIFFERS_FROM_REFERENCE, LARGE_EVAL_DIFF_VS_REFERENCE |
| 142 | h1h3 (+818cp) | h1h3 (+821cp) | h1h4 (+498cp) | MOVE_DIFFERS_FROM_REFERENCE, LARGE_EVAL_DIFF_VS_REFERENCE |

---

## Detailed Position Analysis


### Position 135

**FEN:** `7R/8/8/8/8/3k4/3p4/3K4 b - - 1 1`

**Analysis Results:**
- **Baseline:** d3d4 (-815cp)
- **Extended:** d3d4 (-797cp)
- **Reference:** d3e4 (-448cp)

**Principal Variations:**
- **Baseline PV:** d3d4 h8h2 d4c3 h2d2 c3b3 d2g2 b3c4 g2g8
- **Extended PV:** d3d4 h8h5 d4d3 h5h4 d3e3 h4g4 e3d3 g4g2
- **Reference PV:** d3e4 h8h7 e4d3 h7d7 d3e4 d7e7 e4d4 e7e8

**Critical Issues:**
- Move differs from Stockfish: d3d4 vs d3e4
- Evaluation differs from Stockfish by 367cp

---
### Position 136

**FEN:** `8/8/8/8/8/3K4/3P4/3k3r b - - 0 1`

**Analysis Results:**
- **Baseline:** h1h3 (+811cp)
- **Extended:** h1h3 (+819cp)
- **Reference:** h1h4 (+472cp)

**Principal Variations:**
- **Baseline PV:** h1h3 d3d4 d1d2 d4e4 h3g3 e4f4 g3b3 f4e4
- **Extended PV:** h1h3 d3c4 d1d2 c4b4 h3h4 b4b5 h4g4 b5c5
- **Reference PV:** h1h4 d3e3 d1c2 d2d4 c2c3 d4d5 c3c4 d5d6

**Critical Issues:**
- Move differs from Stockfish: h1h3 vs h1h4
- Evaluation differs from Stockfish by 339cp

---
### Position 137

**FEN:** `8/8/8/8/8/8/3PK3/2k4r b - - 2 2`

**Analysis Results:**
- **Baseline:** h1h2 (+805cp)
- **Extended:** h1h2 (+818cp)
- **Reference:** h1h3 (+728cp)

**Principal Variations:**
- **Baseline PV:** h1h2 e2d3 h2d2 d3c3 d2d6 c3c4 d6d7 c4c3
- **Extended PV:** h1h2
- **Reference PV:** h1h3 d2d4 c1c2 d4d5 h3d3 d5d6 c2c3 d6d7

**Critical Issues:**
- Move differs from Stockfish: h1h2 vs h1h3

---
### Position 138

**FEN:** `8/8/8/7r/8/3K4/3P4/3k4 w - - 1 2`

**Analysis Results:**
- **Baseline:** d3c3 (-825cp)
- **Extended:** d3e3 (-823cp)
- **Reference:** d3c3 (-479cp)

**Principal Variations:**
- **Baseline PV:** d3c3 h5h3 d2d3 d1e2 c3d4 h3d3 d4e4 d3d1
- **Extended PV:** d3e3 h5h3 e3f4 d1d2 f4e4 d2e1 e4f4 e1f1
- **Reference PV:** d3c3 d1e2 d2d3 e2e3 c3c4 h5f5 d3d4 e3e4

**Critical Issues:**
- Move changes from d3c3 to d3e3 with deeper search
- Evaluation differs from Stockfish by 346cp

---
### Position 139

**FEN:** `7r/8/8/8/8/3K4/3P4/3k4 w - - 1 2`

**Analysis Results:**
- **Baseline:** d3e3 (-829cp)
- **Extended:** d3e3 (-825cp)
- **Reference:** d3e4 (-473cp)

**Principal Variations:**
- **Baseline PV:** d3e3 h8h3 e3e4 d1d2 e4f4 d2e1 f4g4 h3h8
- **Extended PV:** d3e3 h8h3
- **Reference PV:** d3e4 d1d2 e4e5 d2c3 e5f6 c3c4 f6e6 h8h3

**Critical Issues:**
- Move differs from Stockfish: d3e3 vs d3e4
- Evaluation differs from Stockfish by 356cp

---
### Position 140

**FEN:** `8/8/8/8/3K4/8/3P4/2k4r b - - 2 2`

**Analysis Results:**
- **Baseline:** c1d2 (+811cp)
- **Extended:** c1d2 (+812cp)
- **Reference:** c1d2 (+455cp)

**Principal Variations:**
- **Baseline PV:** c1d2 d4e4 h1h4 e4f5 d2c1 f5e5 c1b1 e5e6
- **Extended PV:** c1d2 d4e4 h1h4 e4e5 d2c1 e5d5 h4a4 d5e5
- **Reference PV:** c1d2 d4e5 d2e3 e5e6 h1d1 e6e5 e3f3 e5f5

**Critical Issues:**
- Evaluation differs from Stockfish by 356cp

---
### Position 141

**FEN:** `8/8/8/8/7r/2K5/3P4/3k4 b - - 2 2`

**Analysis Results:**
- **Baseline:** h4h3 (+810cp)
- **Extended:** h4h3 (+822cp)
- **Reference:** d1e2 (+531cp)

**Principal Variations:**
- **Baseline PV:** h4h3 d2d3 d1e2 c3d4 h3d3 d4e4 d3e3 e4f4
- **Extended PV:** h4h3 d2d3 d1e2 c3d4 h3d3 d4e4 d3e3
- **Reference PV:** d1e2 d2d4 h4h6 c3c4 e2e3 d4d5 e3e4 d5d6

**Critical Issues:**
- Move differs from Stockfish: h4h3 vs d1e2
- Evaluation differs from Stockfish by 279cp

---
### Position 142

**FEN:** `8/8/8/8/8/2K5/3P4/4k2r b - - 2 2`

**Analysis Results:**
- **Baseline:** h1h3 (+818cp)
- **Extended:** h1h3 (+821cp)
- **Reference:** h1h4 (+498cp)

**Principal Variations:**
- **Baseline PV:** h1h3 c3d4 e1d2 d4d5 d2e2 d5d4 h3a3 d4e4
- **Extended PV:** h1h3
- **Reference PV:** h1h4 c3d3 e1f2 d3c2 h4h3 d2d3 f2e3 c2c3

**Critical Issues:**
- Move differs from Stockfish: h1h3 vs h1h4
- Evaluation differs from Stockfish by 320cp

---

## Key Findings

### Issues Summary
- **MOVE_DIFFERS_FROM_REFERENCE:** 6 positions
- **LARGE_EVAL_DIFF_VS_REFERENCE:** 7 positions
- **MOVE_CHANGE_WITH_DEPTH:** 1 positions


### Recommendations
1. **Manual Review:** Each flagged position requires expert analysis
2. **Evaluation Tuning:** Focus on positions with large evaluation discrepancies  
3. **Search Improvements:** Address depth-dependent move changes
4. **Reference Alignment:** Investigate moves that differ from Stockfish

---

*Analysis completed: 2025-09-11 19:30:46*
