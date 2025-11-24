# Phase 2: Evaluation Component Comparison Tool - Usage Guide

## Overview

The **Evaluation Component Comparison Tool** (`evaluation_component_comparison.py`) performs detailed analysis of tactical positions to identify specific parameter discrepancies between RubiChess and Stockfish.

## Features

### ✅ Implemented
- **Dual Engine Communication**: Interfaces with both RubiChess and Stockfish
- **Stockfish Eval Parsing**: Extracts NNUE evaluation components (PSQT, Positional, Buckets)
- **RubiChess Analysis**: Runs engine analysis and extracts evaluation scores
- **Automated Comparison**: Analyzes positions 60, 98, and 103
- **Report Generation**: Creates detailed markdown reports with recommendations

### 🔄 Requires Enhancement
- **RubiChess Trace Parsing**: Full component extraction (Material, Mobility, Threats, etc.)
  - Currently extracts only final evaluation
  - Needs parsing of detailed trace output from `traceEvalOut()`
- **Component Mapping**: More sophisticated mapping between RubiChess and Stockfish components

## Prerequisites

### 1. Engine Paths
Update paths in the script if different:
```python
self.rubichess_path = r"..\RubiChess\x64\Release\RubiChess.exe"
self.stockfish_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
```

### 2. RubiChess Trace Output (Optional Enhancement)
For full component analysis, RubiChess may need:
- Compilation with `TRACE` flag enabled
- Special UCI commands to enable trace output
- Or separate tool to extract trace data

### 3. Python Dependencies
```bash
pip install python-chess  # If needed for board manipulation
```

## Usage

### Basic Run
```bash
cd d:\Windsurf\RubiChessAdvanced\analysis
python evaluation_component_comparison.py
```

### Expected Output
```
================================================================================
PHASE 2: EVALUATION COMPONENT COMPARISON TOOL
================================================================================

This tool analyzes tactical positions to identify specific parameter
discrepancies between RubiChess and Stockfish evaluations.

Target Positions:
  Position 60: r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/3PbN2...
  Position 98: 8/8/2k5/5p2/6p1/2K5/3P4/8 b - - 1 1...
  Position 103: 8/8/1p1k4/3p4/3P4/1P6/4K3/8 b - - 1...

Press Enter to begin analysis...

================================================================================
Analyzing Position 60
FEN: r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/3PbN2/PPP2PPP/RNBQ1RK1 w kq - 1 6
================================================================================

[1/2] Running RubiChess evaluation...
[2/2] Running Stockfish evaluation...

================================================================================
EVALUATION COMPARISON
================================================================================
RubiChess:   +488 cp
Stockfish:   +741 cp
Difference:  -253 cp (RubiChess underevaluates)

... (similar for other positions)

[OK] Report generated: phase2_component_analysis.md
```

## Target Positions

### Position 60: Opening Tactical Position
```
FEN: r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/3PbN2/PPP2PPP/RNBQ1RK1 w kq - 1 6
Issue: RubiChess +488cp vs Stockfish +741cp (-253cp difference)
Focus: Tactical evaluation in complex opening position
```

### Position 98: Endgame Pawn Position
```
FEN: 8/8/2k5/5p2/6p1/2K5/3P4/8 b - - 1 1
Issue: Different evaluation of pawn endgame
Focus: Pawn structure and king activity
```

### Position 103: Simple Endgame
```
FEN: 8/8/1p1k4/3p4/3P4/1P6/4K3/8 b - - 1 1
Issue: Symmetric pawn structure evaluation
Focus: Material and positional balance
```

## Output Files

### 1. phase2_component_analysis.md
Comprehensive analysis report containing:
- Executive summary with averages
- Detailed analysis per position
- Component discrepancies
- Specific recommendations
- Next steps

### 2. Console Output
Real-time progress and results

## Interpreting Results

### Evaluation Difference
```
Difference: -253 cp (RubiChess underevaluates)
```
- **Positive**: RubiChess evaluates position higher than Stockfish
- **Negative**: RubiChess evaluates position lower than Stockfish
- **>100cp**: Significant discrepancy requiring attention
- **>200cp**: Critical discrepancy requiring major adjustments

### Component Discrepancies
```
Component Discrepancies:
- Material: +15.0cp
- Positional: -45.0cp
```
Shows which evaluation components differ most significantly.

### Recommendations
Actionable suggestions for parameter tuning:
- CRITICAL: >200cp difference
- MEDIUM: 100-200cp difference
- MINOR: <100cp difference

## Enhancing the Tool

### Adding Full RubiChess Trace Support

To get detailed component breakdown from RubiChess:

1. **Check if RubiChess supports trace output:**
   ```cpp
   // In RubiChess source, look for TRACE or DEBUG flags
   // Check eval.cpp for traceEvalOut() function
   ```

2. **Modify the tool to capture trace:**
   ```python
   # Add special command or flag to enable trace
   process.stdin.write("setoption name Debug type true\n")
   # Or compile RubiChess with TRACE enabled
   ```

3. **Parse full trace output:**
   ```python
   def _parse_rubichess_trace(self, lines):
       # Parse lines like:
       # "Material | +50 +30 | ..."
       # "Mobility | +40 +20 | ..."
       # Extract all components
   ```

### Adding More Positions

Add to `target_positions` dict:
```python
self.target_positions = {
    60: "fen_string_1",
    98: "fen_string_2",
    103: "fen_string_3",
    120: "new_position_fen",  # Add more
}
```

### Customizing Depth

Change analysis depth:
```python
rubichess_trace = self.run_rubichess_trace(fen, depth=20)  # Default is 15
```

## Troubleshooting

### Engine Not Found
```
Error running RubiChess: [WinError 2] The system cannot find the file specified
```
**Solution**: Update engine paths in `__init__` method

### No Trace Output
```
[WARNING] Limited component data available
```
**Solution**: RubiChess may need special compilation or commands for full trace output

### Stockfish eval Command Not Responding
```
Error running Stockfish eval: timeout
```
**Solution**: Increase timeout in `run_stockfish_eval` method

## Next Steps After Analysis

1. **Review Generated Report**
   - Open `phase2_component_analysis.md`
   - Identify consistent patterns across positions
   - Note largest discrepancies

2. **Prioritize Parameters to Tune**
   - Focus on components with >50cp differences
   - Start with highest-impact changes
   - Test incrementally

3. **Implement Changes**
   - Modify `src/RubiChess.h` evaluation parameters
   - Document each change
   - Test after each modification

4. **Validate**
   - Re-run this tool after changes
   - Verify improvements
   - Check for regressions on Phase 1 positions

## Support

For issues or enhancements:
1. Check RubiChess source code for trace capabilities
2. Verify engine paths and UCI compatibility
3. Review console output for specific error messages

---

**Status**: ✅ Tool Ready for Use
**Next**: Run analysis and review results
