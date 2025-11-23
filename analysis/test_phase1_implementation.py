#!/usr/bin/env python3
"""
Test script for Phase 1 RubiChess endgame optimization implementation.
Tests the modified engine against the 8 critical positions (135-142).
"""

import chess
import chess.engine
import chess.pgn
import json
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any
import time

def load_positions_from_pgn(pgn_file: str, start_pos: int = 135, end_pos: int = 142) -> List[Dict]:
    """Load specific positions from PGN file."""
    positions = []
    
    try:
        with open(pgn_file, 'r') as f:
            game_num = 0
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                game_num += 1
                if start_pos <= game_num <= end_pos:
                    board = game.board()
                    for move in game.mainline_moves():
                        board.push(move)
                    
                    positions.append({
                        'position_id': game_num,
                        'fen': board.fen(),
                        'board': board.copy(),
                        'description': f"Position {game_num} - {game.headers.get('Event', 'Unknown')}"
                    })
                
                if game_num > end_pos:
                    break
                    
    except Exception as e:
        print(f"Error loading positions: {e}")
        return []
    
    return positions

def analyze_with_engine(board: chess.Board, engine_path: str, engine_name: str, depth: int = 15, time_limit: float = 8.0) -> Dict:
    """Analyze position with specified engine."""
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
                'pv': pv_moves,
                'nodes': result.get('nodes', 0),
                'time': result.get('time', 0),
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
            'success': False,
            'error': str(e)
        }

def test_phase1_implementation():
    """Test the Phase 1 implementation against critical positions."""
    
    # Configuration
    pgn_file = "comprehensive_positions.pgn"
    original_engine = r"..\RubiChess\x64\Release\RubiChess.exe"
    modified_engine = r"..\RubiChess\src\Release-modified\RubiChess_1.1_dev_20250911_001_x86-64-avx2.exe"
    stockfish_engine = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
    
    print("=== Phase 1 RubiChess Endgame Optimization Test ===")
    print(f"Testing positions 135-142 from {pgn_file}")
    print()
    
    # Load positions
    positions = load_positions_from_pgn(pgn_file, 135, 142)
    if not positions:
        print("ERROR: Could not load test positions!")
        return
    
    print(f"Loaded {len(positions)} positions for testing")
    print()
    
    # Test results storage
    results = []
    
    for pos_data in positions:
        pos_id = pos_data['position_id']
        board = pos_data['board']
        fen = pos_data['fen']
        
        print(f"Testing Position {pos_id}:")
        print(f"FEN: {fen}")
        
        # Analyze with original RubiChess (if available)
        original_result = None
        if Path(original_engine).exists():
            print("  Analyzing with original RubiChess...")
            original_result = analyze_with_engine(board, original_engine, "RubiChess_Original")
        
        # Analyze with modified RubiChess
        print("  Analyzing with modified RubiChess...")
        modified_result = analyze_with_engine(board, modified_engine, "RubiChess_Modified")
        
        # Analyze with Stockfish (reference)
        print("  Analyzing with Stockfish (reference)...")
        stockfish_result = analyze_with_engine(board, stockfish_engine, "Stockfish")
        
        # Store results
        result_entry = {
            'position_id': pos_id,
            'fen': fen,
            'description': pos_data['description'],
            'original': original_result,
            'modified': modified_result,
            'stockfish': stockfish_result
        }
        results.append(result_entry)
        
        # Print comparison
        if modified_result['success'] and stockfish_result['success']:
            eval_diff = abs(modified_result['evaluation'] - stockfish_result['evaluation']) if modified_result['evaluation'] and stockfish_result['evaluation'] else None
            move_match = modified_result['move'] == stockfish_result['move']
            
            print(f"  Modified RubiChess: {modified_result['evaluation']}cp, move: {modified_result['move']}")
            print(f"  Stockfish:          {stockfish_result['evaluation']}cp, move: {stockfish_result['move']}")
            print(f"  Evaluation diff:    {eval_diff}cp")
            print(f"  Move agreement:     {move_match}")
            
            if original_result and original_result['success']:
                orig_eval_diff = abs(original_result['evaluation'] - stockfish_result['evaluation']) if original_result['evaluation'] and stockfish_result['evaluation'] else None
                print(f"  Original vs SF:     {orig_eval_diff}cp")
                
                if eval_diff and orig_eval_diff:
                    improvement = orig_eval_diff - eval_diff
                    print(f"  Improvement:        {improvement:+.0f}cp")
        
        print()
    
    # Generate summary report
    print("=== PHASE 1 TEST SUMMARY ===")
    
    successful_tests = [r for r in results if r['modified']['success'] and r['stockfish']['success']]
    total_tests = len(results)
    
    if successful_tests:
        # Calculate metrics
        eval_diffs = []
        move_agreements = 0
        improvements = []
        
        for result in successful_tests:
            mod_eval = result['modified']['evaluation']
            sf_eval = result['stockfish']['evaluation']
            
            if mod_eval is not None and sf_eval is not None:
                eval_diff = abs(mod_eval - sf_eval)
                eval_diffs.append(eval_diff)
                
                # Check for improvement vs original
                if result['original'] and result['original']['success'] and result['original']['evaluation'] is not None:
                    orig_diff = abs(result['original']['evaluation'] - sf_eval)
                    improvement = orig_diff - eval_diff
                    improvements.append(improvement)
            
            if result['modified']['move'] == result['stockfish']['move']:
                move_agreements += 1
        
        avg_eval_diff = sum(eval_diffs) / len(eval_diffs) if eval_diffs else 0
        move_agreement_pct = (move_agreements / len(successful_tests)) * 100
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        print(f"Successful tests: {len(successful_tests)}/{total_tests}")
        print(f"Average evaluation difference vs Stockfish: {avg_eval_diff:.1f}cp")
        print(f"Move agreement with Stockfish: {move_agreement_pct:.1f}% ({move_agreements}/{len(successful_tests)})")
        if improvements:
            print(f"Average improvement over original: {avg_improvement:+.1f}cp")
        
        # Save detailed results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = f"phase1_test_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Detailed results saved to: {json_file}")
        
        # Save CSV summary
        csv_file = f"phase1_test_summary_{timestamp}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Position', 'FEN', 'Modified_Eval', 'Modified_Move', 'Stockfish_Eval', 'Stockfish_Move', 'Eval_Diff', 'Move_Match', 'Original_Eval', 'Improvement'])
            
            for result in results:
                if result['modified']['success'] and result['stockfish']['success']:
                    mod_eval = result['modified']['evaluation']
                    sf_eval = result['stockfish']['evaluation']
                    eval_diff = abs(mod_eval - sf_eval) if mod_eval and sf_eval else None
                    move_match = result['modified']['move'] == result['stockfish']['move']
                    
                    orig_eval = result['original']['evaluation'] if result['original'] and result['original']['success'] else None
                    improvement = None
                    if orig_eval and sf_eval and mod_eval:
                        improvement = abs(orig_eval - sf_eval) - abs(mod_eval - sf_eval)
                    
                    writer.writerow([
                        result['position_id'],
                        result['fen'],
                        mod_eval,
                        result['modified']['move'],
                        sf_eval,
                        result['stockfish']['move'],
                        eval_diff,
                        move_match,
                        orig_eval,
                        improvement
                    ])
        
        print(f"Summary CSV saved to: {csv_file}")
    
    else:
        print("ERROR: No successful test results to analyze!")

if __name__ == "__main__":
    test_phase1_implementation()
