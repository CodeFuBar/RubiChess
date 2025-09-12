#!/usr/bin/env python3
"""
Deep Dive Analysis for Positions 135-142 using proven engine analysis method.
"""

import chess
import chess.pgn
import chess.engine
import csv
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def analyze_with_engine(board: chess.Board, engine_path: str, engine_name: str, depth: int = 15, time_limit: float = 8.0) -> Dict:
    """Analyze position with engine using robust approach."""
    try:
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            # Configure engine
            try:
                engine.configure({"Hash": 256})
            except:
                pass
            
            # Analyze position
            result = engine.analyse(board, chess.engine.Limit(depth=depth, time=time_limit))
            
            # Extract move and evaluation
            best_move = result['pv'][0] if result.get('pv') else None
            pv_moves = [str(move) for move in result.get('pv', [])]
            
            # Handle evaluation
            eval_cp = None
            if result.get('score'):
                score = result['score']
                if score.is_mate():
                    mate_in = score.mate()
                    eval_cp = 10000 - abs(mate_in) * 10 if mate_in > 0 else -10000 + abs(mate_in) * 10
                else:
                    eval_cp = score.relative.score(mate_score=10000)
            
            return {
                'move': str(best_move) if best_move else None,
                'evaluation': eval_cp,
                'pv': pv_moves,
                'nodes': result.get('nodes', 0),
                'time': result.get('time', 0),
                'success': True
            }
            
    except Exception as e:
        return {
            'move': None,
            'evaluation': None,
            'pv': [],
            'nodes': 0,
            'time': 0,
            'success': False,
            'error': str(e)
        }

def load_critical_positions(pgn_filename: str, target_positions: List[int]) -> Dict[int, chess.Board]:
    """Load specific positions from PGN file."""
    positions = {}
    
    print(f"Loading positions {target_positions} from {pgn_filename}...")
    
    with open(pgn_filename, 'r', encoding='utf-8') as f:
        position_num = 1
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            
            if position_num in target_positions:
                board = game.board()
                if game.headers.get("FEN"):
                    board.set_fen(game.headers["FEN"])
                
                positions[position_num] = board
                print(f"  Position {position_num}: {board.fen()}")
            
            position_num += 1
    
    print(f"Successfully loaded {len(positions)} critical positions")
    return positions

def deep_dive_analysis():
    """Run deep dive analysis on positions 135-142."""
    
    # Engine paths
    rubichess_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\RubiChess-avx2\RubiChess.exe"
    stockfish_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
    
    # Target positions (worst performers)
    target_positions = [135, 136, 137, 138, 139, 140, 141, 142]
    
    # Analysis settings
    baseline_depth = 15
    baseline_time = 8.0
    extended_depth = 25
    extended_time = 20.0
    reference_depth = 20
    reference_time = 15.0
    
    print("="*80)
    print("DEEP DIVE ANALYSIS: POSITIONS 135-142")
    print("="*80)
    
    # Step 1: Load positions
    positions = load_critical_positions('weakness_test_positions.pgn', target_positions)
    
    if not positions:
        print("ERROR: No positions loaded. Exiting.")
        return
    
    # Results storage
    results = {}
    
    # Step 2-6: Comprehensive analysis for each position
    for pos_id, board in positions.items():
        print(f"\n{'='*60}")
        print(f"ANALYZING POSITION {pos_id}")
        print(f"{'='*60}")
        print(f"FEN: {board.fen()}")
        
        result = {'position_id': pos_id, 'fen': board.fen()}
        
        # Baseline analysis
        print(f"\n[BASELINE] Depth {baseline_depth}, Time {baseline_time}s")
        baseline_result = analyze_with_engine(board, rubichess_path, "RubiChess", baseline_depth, baseline_time)
        
        if baseline_result['success']:
            print(f"  RubiChess: {baseline_result['move']} ({baseline_result['evaluation']:+}cp)")
            print(f"  PV: {' '.join(baseline_result['pv'][:6])}")
            print(f"  Nodes: {baseline_result['nodes']:,}, Time: {baseline_result['time']:.2f}s")
        else:
            print(f"  RubiChess: FAILED - {baseline_result.get('error', 'Unknown error')}")
        
        result['baseline'] = baseline_result
        
        # Extended analysis
        print(f"\n[EXTENDED] Depth {extended_depth}, Time {extended_time}s")
        extended_result = analyze_with_engine(board, rubichess_path, "RubiChess", extended_depth, extended_time)
        
        if extended_result['success']:
            print(f"  RubiChess: {extended_result['move']} ({extended_result['evaluation']:+}cp)")
            print(f"  PV: {' '.join(extended_result['pv'][:6])}")
            print(f"  Nodes: {extended_result['nodes']:,}, Time: {extended_result['time']:.2f}s")
        else:
            print(f"  RubiChess: FAILED - {extended_result.get('error', 'Unknown error')}")
        
        result['extended'] = extended_result
        
        # Reference analysis
        print(f"\n[REFERENCE] Stockfish Depth {reference_depth}, Time {reference_time}s")
        reference_result = analyze_with_engine(board, stockfish_path, "Stockfish", reference_depth, reference_time)
        
        if reference_result['success']:
            print(f"  Stockfish: {reference_result['move']} ({reference_result['evaluation']:+}cp)")
            print(f"  PV: {' '.join(reference_result['pv'][:6])}")
            print(f"  Nodes: {reference_result['nodes']:,}, Time: {reference_result['time']:.2f}s")
        else:
            print(f"  Stockfish: FAILED - {reference_result.get('error', 'Unknown error')}")
        
        result['reference'] = reference_result
        
        # Analysis comparison
        print(f"\n[COMPARISON]")
        flags = []
        issues = []
        
        if baseline_result['success'] and extended_result['success']:
            # Self-comparison
            moves_differ = baseline_result['move'] != extended_result['move']
            eval_swing = abs(baseline_result['evaluation'] - extended_result['evaluation']) if baseline_result['evaluation'] and extended_result['evaluation'] else 0
            
            print(f"  Baseline vs Extended:")
            print(f"    Moves: {baseline_result['move']} vs {extended_result['move']} ({'DIFFER' if moves_differ else 'AGREE'})")
            print(f"    Eval swing: {eval_swing}cp")
            
            if moves_differ:
                flags.append("MOVE_CHANGE_WITH_DEPTH")
                issues.append(f"Move changes from {baseline_result['move']} to {extended_result['move']} with deeper search")
            
            if eval_swing > 50:
                flags.append("LARGE_EVAL_SWING")
                issues.append(f"Evaluation swings {eval_swing}cp between depths")
        
        if baseline_result['success'] and reference_result['success']:
            # Reference comparison
            ref_move_diff = baseline_result['move'] != reference_result['move']
            ref_eval_diff = abs(baseline_result['evaluation'] - reference_result['evaluation']) if baseline_result['evaluation'] and reference_result['evaluation'] else 0
            
            print(f"  Baseline vs Reference:")
            print(f"    Moves: {baseline_result['move']} vs {reference_result['move']} ({'DIFFER' if ref_move_diff else 'AGREE'})")
            print(f"    Eval diff: {ref_eval_diff}cp")
            
            if ref_move_diff:
                flags.append("MOVE_DIFFERS_FROM_REFERENCE")
                issues.append(f"Move differs from Stockfish: {baseline_result['move']} vs {reference_result['move']}")
            
            if ref_eval_diff > 100:
                flags.append("LARGE_EVAL_DIFF_VS_REFERENCE")
                issues.append(f"Evaluation differs from Stockfish by {ref_eval_diff}cp")
        
        result['flags'] = flags
        result['issues'] = issues
        
        print(f"  Detected Issues: {len(flags)}")
        for issue in issues:
            print(f"    - {issue}")
        
        results[pos_id] = result
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("GENERATING SUMMARY REPORT")
    print(f"{'='*80}")
    
    # CSV Summary
    csv_data = []
    for pos_id, result in results.items():
        baseline = result.get('baseline', {})
        extended = result.get('extended', {})
        reference = result.get('reference', {})
        
        csv_row = {
            'Position': pos_id,
            'FEN': result['fen'],
            'Baseline_Move': baseline.get('move', 'N/A'),
            'Baseline_Eval': baseline.get('evaluation', 'N/A'),
            'Extended_Move': extended.get('move', 'N/A'),
            'Extended_Eval': extended.get('evaluation', 'N/A'),
            'Reference_Move': reference.get('move', 'N/A'),
            'Reference_Eval': reference.get('evaluation', 'N/A'),
            'Issues': '; '.join(result.get('issues', [])),
            'Flags': ', '.join(result.get('flags', []))
        }
        csv_data.append(csv_row)
    
    # Save CSV
    with open('deep_dive_summary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Position', 'FEN', 'Baseline_Move', 'Baseline_Eval', 'Extended_Move', 'Extended_Eval', 
                     'Reference_Move', 'Reference_Eval', 'Issues', 'Flags']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    # Save detailed JSON
    with open('deep_dive_detailed.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, indent=2, default=str)
    
    # Generate markdown report
    markdown_content = f"""# Deep Dive Analysis: Positions 135-142
## Critical Evaluation Failure Investigation

### Executive Summary

Deep dive analysis of the 8 worst-performing positions from large-scale weakness testing.

**Positions Analyzed:** {', '.join(map(str, target_positions))}
**Analysis Completed:** {len(results)}/{len(target_positions)} positions

---

## Summary Table

| Position | Baseline Move/Eval | Extended Move/Eval | Reference Move/Eval | Critical Issues |
|----------|-------------------|-------------------|-------------------|-----------------|"""

    for row in csv_data:
        pos = row['Position']
        baseline_move = row['Baseline_Move']
        baseline_eval = f"{row['Baseline_Eval']:+}cp" if isinstance(row['Baseline_Eval'], (int, float)) else 'N/A'
        extended_move = row['Extended_Move']
        extended_eval = f"{row['Extended_Eval']:+}cp" if isinstance(row['Extended_Eval'], (int, float)) else 'N/A'
        reference_move = row['Reference_Move']
        reference_eval = f"{row['Reference_Eval']:+}cp" if isinstance(row['Reference_Eval'], (int, float)) else 'N/A'
        flags = row['Flags']
        
        markdown_content += f"""
| {pos} | {baseline_move} ({baseline_eval}) | {extended_move} ({extended_eval}) | {reference_move} ({reference_eval}) | {flags} |"""

    markdown_content += f"""

---

## Detailed Position Analysis

"""

    for pos_id, result in results.items():
        baseline = result.get('baseline', {})
        extended = result.get('extended', {})
        reference = result.get('reference', {})
        
        markdown_content += f"""
### Position {pos_id}

**FEN:** `{result['fen']}`

**Analysis Results:**
- **Baseline:** {baseline.get('move', 'N/A')} ({f"{baseline.get('evaluation'):+}cp" if isinstance(baseline.get('evaluation'), (int, float)) else 'N/A'})
- **Extended:** {extended.get('move', 'N/A')} ({f"{extended.get('evaluation'):+}cp" if isinstance(extended.get('evaluation'), (int, float)) else 'N/A'})
- **Reference:** {reference.get('move', 'N/A')} ({f"{reference.get('evaluation'):+}cp" if isinstance(reference.get('evaluation'), (int, float)) else 'N/A'})

**Principal Variations:**
- **Baseline PV:** {' '.join(baseline.get('pv', [])[:8])}
- **Extended PV:** {' '.join(extended.get('pv', [])[:8])}
- **Reference PV:** {' '.join(reference.get('pv', [])[:8])}

**Critical Issues:**
{chr(10).join([f'- {issue}' for issue in result.get('issues', ['None detected'])])}

---"""

    markdown_content += f"""

## Key Findings

### Issues Summary
"""

    # Count issues across all positions
    all_flags = []
    all_issues = []
    for result in results.values():
        all_flags.extend(result.get('flags', []))
        all_issues.extend(result.get('issues', []))
    
    flag_counts = {}
    for flag in all_flags:
        flag_counts[flag] = flag_counts.get(flag, 0) + 1
    
    for flag, count in flag_counts.items():
        markdown_content += f"- **{flag}:** {count} positions\n"

    markdown_content += f"""

### Recommendations
1. **Manual Review:** Each flagged position requires expert analysis
2. **Evaluation Tuning:** Focus on positions with large evaluation discrepancies  
3. **Search Improvements:** Address depth-dependent move changes
4. **Reference Alignment:** Investigate moves that differ from Stockfish

---

*Analysis completed: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""

    with open('deep_dive_report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Summary saved to: deep_dive_summary.csv")
    print(f"Detailed results saved to: deep_dive_detailed.json")
    print(f"Report saved to: deep_dive_report.md")
    
    print(f"\n{'='*80}")
    print("DEEP DIVE ANALYSIS COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    deep_dive_analysis()
