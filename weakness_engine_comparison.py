#!/usr/bin/env python3
"""
Large-scale engine comparison on 491 weakness-focused positions using proven approach.
"""

import chess
import chess.pgn
import chess.engine
import csv
import time
import os
import sys
from pathlib import Path
from typing import List, Tuple

# Engine paths
RUBICHESS_PATH = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\RubiChess-avx2\RubiChess.exe"
STOCKFISH_PATH = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"

def load_positions_from_pgn(filename: str) -> List[Tuple[int, chess.Board]]:
    """Load positions from PGN file."""
    positions = []
    
    print(f"Loading positions from {filename}...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        position_num = 1
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            
            board = game.board()
            if game.headers.get("FEN"):
                board.set_fen(game.headers["FEN"])
            
            positions.append((position_num, board))
            position_num += 1
    
    print(f"Loaded {len(positions)} positions")
    return positions

def analyze_single_position(engine_path, engine_name, fen, position_id, depth=15, time_limit=8.0):
    """Analyze single position with fresh engine instance"""
    try:
        # Create fresh engine instance
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        
        board = chess.Board(fen)
        limit = chess.engine.Limit(depth=depth, time=time_limit)
        
        start_time = time.time()
        result = engine.analyse(board, limit)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Extract results
        best_move = str(result.get('pv', [None])[0]) if result.get('pv') else 'none'
        evaluation = result['score'].relative.score(mate_score=10000) if result.get('score') else 0
        nodes = result.get('nodes', 0)
        
        # Close engine
        engine.quit()
        
        return {
            'success': True,
            'move': best_move,
            'evaluation': evaluation,
            'nodes': nodes,
            'time': analysis_time
        }
        
    except Exception as e:
        try:
            engine.quit()
        except:
            pass
        return {
            'success': False,
            'move': 'none',
            'evaluation': 0,
            'nodes': 0,
            'time': 0,
            'error': str(e)
        }

def analyze_positions(positions: List[Tuple[int, chess.Board]]):
    """Analyze all positions with both engines."""
    results = []
    total_positions = len(positions)
    
    rubichess_successes = 0
    stockfish_successes = 0
    move_agreements = 0
    large_eval_diffs = 0
    
    print(f"\n=== Starting analysis of {total_positions} positions ===")
    print(f"RubiChess: {RUBICHESS_PATH}")
    print(f"Stockfish: {STOCKFISH_PATH}")
    print()
    
    for position_num, board in positions:
        print(f"[{position_num}/{total_positions}] Analyzing position {position_num}...")
        
        fen = board.fen()
        
        # Analyze with RubiChess
        print("  RubiChess analyzing...")
        rubichess_result = analyze_single_position(RUBICHESS_PATH, "RubiChess", fen, position_num)
        
        if rubichess_result['success']:
            print(f"    RubiChess: {rubichess_result['move']} ({rubichess_result['evaluation']:+}cp) - {rubichess_result['time']:.2f}s")
            rubichess_successes += 1
        else:
            print(f"    RubiChess: Failed")
        
        # Analyze with Stockfish
        print("  Stockfish analyzing...")
        stockfish_result = analyze_single_position(STOCKFISH_PATH, "Stockfish", fen, position_num)
        
        if stockfish_result['success']:
            print(f"    Stockfish: {stockfish_result['move']} ({stockfish_result['evaluation']:+}cp) - {stockfish_result['time']:.2f}s")
            stockfish_successes += 1
        else:
            print(f"    Stockfish: Failed")
        
        # Compare results
        if rubichess_result['success'] and stockfish_result['success']:
            moves_agree = rubichess_result['move'] == stockfish_result['move']
            if moves_agree:
                move_agreements += 1
            
            eval_diff = abs(rubichess_result['evaluation'] - stockfish_result['evaluation'])
            if eval_diff > 100:
                large_eval_diffs += 1
            
            move_status = "AGREE" if moves_agree else "DIFFER"
            print(f"    Comparison: {eval_diff}cp difference, moves {move_status}")
        
        # Store result
        result = {
            'position': position_num,
            'fen': fen,
            'rubichess_move': rubichess_result['move'],
            'rubichess_eval': rubichess_result['evaluation'],
            'rubichess_nodes': rubichess_result['nodes'],
            'rubichess_time': rubichess_result['time'],
            'rubichess_success': rubichess_result['success'],
            'stockfish_move': stockfish_result['move'],
            'stockfish_eval': stockfish_result['evaluation'],
            'stockfish_nodes': stockfish_result['nodes'],
            'stockfish_time': stockfish_result['time'],
            'stockfish_success': stockfish_result['success']
        }
        results.append(result)
        
        # Save progress every 25 positions
        if position_num % 25 == 0:
            save_results_to_csv(results, f'large_scale_progress_{position_num}.csv')
            
            # Print progress statistics
            successful_comparisons = min(rubichess_successes, stockfish_successes)
            print(f"\n=== PROGRESS STATISTICS ===")
            print(f"Positions analyzed: {position_num}/{total_positions}")
            print(f"RubiChess successful analyses: {rubichess_successes}/{position_num} ({100*rubichess_successes/position_num:.1f}%)")
            print(f"Stockfish successful analyses: {stockfish_successes}/{position_num} ({100*stockfish_successes/position_num:.1f}%)")
            if successful_comparisons > 0:
                print(f"Move agreement: {move_agreements}/{successful_comparisons} ({100*move_agreements/successful_comparisons:.1f}%)")
                print(f"Positions with >100cp difference: {large_eval_diffs}")
            print()
    
    # Final statistics
    successful_comparisons = min(rubichess_successes, stockfish_successes)
    print("\n" + "="*60)
    print("LARGE-SCALE ANALYSIS COMPLETE")
    print("="*60)
    print(f"Total positions: {total_positions}")
    print(f"RubiChess successful analyses: {rubichess_successes}/{total_positions} ({100*rubichess_successes/total_positions:.1f}%)")
    print(f"Stockfish successful analyses: {stockfish_successes}/{total_positions} ({100*stockfish_successes/total_positions:.1f}%)")
    
    if successful_comparisons > 0:
        print(f"\nComparison Statistics:")
        print(f"Successful comparisons: {successful_comparisons}")
        print(f"Move agreement: {move_agreements}/{successful_comparisons} ({100*move_agreements/successful_comparisons:.1f}%)")
        print(f"Positions with >100cp difference: {large_eval_diffs}")
    
    return results

def save_results_to_csv(results, filename):
    """Save results to CSV file."""
    print(f"Saving results to {filename}...")
    
    fieldnames = [
        'position', 'fen',
        'rubichess_move', 'rubichess_eval', 'rubichess_nodes', 'rubichess_time', 'rubichess_success',
        'stockfish_move', 'stockfish_eval', 'stockfish_nodes', 'stockfish_time', 'stockfish_success'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

def main():
    """Main analysis function."""
    print("=== LARGE-SCALE WEAKNESS-FOCUSED ENGINE COMPARISON ===")
    
    # Load positions
    positions = load_positions_from_pgn('weakness_test_positions.pgn')
    
    if not positions:
        print("No positions loaded. Exiting.")
        return
    
    # Analyze positions
    results = analyze_positions(positions)
    
    # Save final results
    save_results_to_csv(results, 'large_scale_engine_comparison.csv')
    
    print(f"\nResults saved to large_scale_engine_comparison.csv")
    print("Ready for comprehensive weakness analysis!")

if __name__ == "__main__":
    main()
