#!/usr/bin/env python3
"""
Focused Phase 1 test comparing original vs modified RubiChess engines
on the available critical endgame positions.
"""

import chess
import chess.engine
import chess.pgn
import json
import csv
import time
from pathlib import Path
from typing import Dict, List

def load_endgame_positions() -> List[Dict]:
    """Load the available endgame positions from PGN."""
    positions = []
    
    try:
        with open('comprehensive_positions.pgn', 'r') as f:
            game_num = 0
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                game_num += 1
                if 135 <= game_num <= 142:  # Target positions
                    board = game.board()
                    for move in game.mainline_moves():
                        board.push(move)
                    
                    positions.append({
                        'position_id': game_num,
                        'fen': board.fen(),
                        'board': board.copy(),
                        'description': f"Position {game_num} - {game.headers.get('Event', 'Endgame Test')}"
                    })
                
                if game_num > 142:
                    break
                    
    except Exception as e:
        print(f"Error loading positions: {e}")
        return []
    
    return positions

def analyze_position(board: chess.Board, engine_path: str, engine_name: str, depth: int = 18, time_limit: float = 10.0) -> Dict:
    """Analyze position with specified engine using deeper search."""
    try:
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            result = engine.analyse(board, chess.engine.Limit(depth=depth, time=time_limit))
            
            best_move = result['pv'][0] if result.get('pv') else None
            pv_moves = [str(move) for move in result.get('pv', [])]
            
            if result.get('score'):
                score = result['score']
                if score.is_mate():
                    mate_in = score.mate()
                    eval_cp = 10000 - abs(mate_in) * 10 if mate_in > 0 else -10000 + abs(mate_in) * 10
                else:
                    eval_cp = score.relative.score(mate_score=10000)
            else:
                eval_cp = None
                
            return {
                'engine': engine_name,
                'move': str(best_move) if best_move else None,
                'evaluation': eval_cp,
                'pv': pv_moves[:5],  # First 5 moves of PV
                'nodes': result.get('nodes', 0),
                'time': result.get('time', 0),
                'depth': result.get('depth', 0),
                'success': True
            }
    except Exception as e:
        return {
            'engine': engine_name,
            'move': None,
            'evaluation': None,
            'pv': [],
            'nodes': 0,
            'time': 0,
            'depth': 0,
            'success': False,
            'error': str(e)
        }

def run_focused_test():
    """Run focused Phase 1 test comparing engines."""
    
    # Engine paths
    original_engine = r"d:\Windsurf\RubiChessAdvanced\RubiChess\x64\Release\RubiChess.exe"
    modified_engine = r"d:\Windsurf\RubiChessAdvanced\RubiChess\src\Release-modified\RubiChess_1.1_dev_20250911_001_x86-64-avx2.exe"
    stockfish_engine = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
    
    print("=== FOCUSED PHASE 1 RUBICHESS ENDGAME TEST ===")
    print("Comparing Original vs Modified RubiChess on critical endgame positions")
    print()
    
    # Load positions
    positions = load_endgame_positions()
    if not positions:
        print("ERROR: Could not load test positions!")
        return
    
    print(f"Loaded {len(positions)} critical endgame positions")
    print()
    
    # Test results
    results = []
    
    for pos_data in positions:
        pos_id = pos_data['position_id']
        board = pos_data['board']
        fen = pos_data['fen']
        
        print(f"=== TESTING POSITION {pos_id} ===")
        print(f"FEN: {fen}")
        print()
        
        # Analyze with original RubiChess
        print("Analyzing with Original RubiChess (depth 18, 10s)...")
        original_result = analyze_position(board, original_engine, "RubiChess_Original")
        
        if original_result['success']:
            print(f"  Move: {original_result['move']}")
            print(f"  Eval: {original_result['evaluation']}cp")
            print(f"  PV: {' '.join(original_result['pv'])}")
            print(f"  Nodes: {original_result['nodes']:,}")
            print(f"  Time: {original_result['time']:.3f}s")
        else:
            print(f"  ERROR: {original_result.get('error', 'Unknown error')}")
        print()
        
        # Analyze with modified RubiChess
        print("Analyzing with Modified RubiChess (depth 18, 10s)...")
        modified_result = analyze_position(board, modified_engine, "RubiChess_Modified")
        
        if modified_result['success']:
            print(f"  Move: {modified_result['move']}")
            print(f"  Eval: {modified_result['evaluation']}cp")
            print(f"  PV: {' '.join(modified_result['pv'])}")
            print(f"  Nodes: {modified_result['nodes']:,}")
            print(f"  Time: {modified_result['time']:.3f}s")
        else:
            print(f"  ERROR: {modified_result.get('error', 'Unknown error')}")
        print()
        
        # Compare results
        if original_result['success'] and modified_result['success']:
            eval_diff = modified_result['evaluation'] - original_result['evaluation'] if both_evals_valid(original_result, modified_result) else None
            move_same = original_result['move'] == modified_result['move']
            
            print("=== COMPARISON ===")
            print(f"Move agreement: {'YES' if move_same else 'NO'}")
            if eval_diff is not None:
                print(f"Evaluation change: {eval_diff:+.0f}cp")
                if abs(eval_diff) > 50:
                    print(f"  -> {'SIGNIFICANT IMPROVEMENT' if eval_diff > 0 else 'SIGNIFICANT CHANGE'}")
            print()
        
        # Store results
        results.append({
            'position_id': pos_id,
            'fen': fen,
            'description': pos_data['description'],
            'original': original_result,
            'modified': modified_result
        })
        
        print("-" * 80)
        print()
    
    # Generate summary
    print("=== PHASE 1 TEST SUMMARY ===")
    
    successful_comparisons = [r for r in results if r['original']['success'] and r['modified']['success']]
    
    if successful_comparisons:
        move_agreements = sum(1 for r in successful_comparisons if r['original']['move'] == r['modified']['move'])
        eval_changes = []
        
        for result in successful_comparisons:
            if both_evals_valid(result['original'], result['modified']):
                eval_change = result['modified']['evaluation'] - result['original']['evaluation']
                eval_changes.append(eval_change)
        
        print(f"Successful comparisons: {len(successful_comparisons)}/{len(results)}")
        print(f"Move agreement: {move_agreements}/{len(successful_comparisons)} ({move_agreements/len(successful_comparisons)*100:.1f}%)")
        
        if eval_changes:
            avg_change = sum(eval_changes) / len(eval_changes)
            significant_improvements = sum(1 for change in eval_changes if change > 50)
            significant_regressions = sum(1 for change in eval_changes if change < -50)
            
            print(f"Average evaluation change: {avg_change:+.1f}cp")
            print(f"Significant improvements (>50cp): {significant_improvements}")
            print(f"Significant regressions (<-50cp): {significant_regressions}")
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # JSON results
        json_file = f"phase1_focused_test_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nDetailed results saved to: {json_file}")
        
        # CSV summary
        csv_file = f"phase1_focused_summary_{timestamp}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Position', 'FEN', 'Original_Move', 'Modified_Move', 'Move_Same', 
                           'Original_Eval', 'Modified_Eval', 'Eval_Change', 'Original_Nodes', 'Modified_Nodes'])
            
            for result in results:
                if result['original']['success'] and result['modified']['success']:
                    orig = result['original']
                    mod = result['modified']
                    eval_change = mod['evaluation'] - orig['evaluation'] if both_evals_valid(orig, mod) else None
                    
                    writer.writerow([
                        result['position_id'],
                        result['fen'],
                        orig['move'],
                        mod['move'],
                        orig['move'] == mod['move'],
                        orig['evaluation'],
                        mod['evaluation'],
                        eval_change,
                        orig['nodes'],
                        mod['nodes']
                    ])
        
        print(f"Summary CSV saved to: {csv_file}")
    
    else:
        print("ERROR: No successful engine comparisons!")

def both_evals_valid(result1: Dict, result2: Dict) -> bool:
    """Check if both results have valid evaluations."""
    return (result1.get('evaluation') is not None and 
            result2.get('evaluation') is not None)

if __name__ == "__main__":
    run_focused_test()
