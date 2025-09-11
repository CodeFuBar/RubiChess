#!/usr/bin/env python3
"""
Robust large-scale engine comparison using the proven approach from comprehensive analysis.
"""

import chess
import chess.engine
import chess.pgn
import csv
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
            best_move = result.pv[0] if result.pv else None
            
            # Handle evaluation
            eval_cp = None
            if result.score:
                if result.score.is_mate():
                    mate_in = result.score.mate()
                    eval_cp = 10000 - abs(mate_in) * 10 if mate_in > 0 else -10000 + abs(mate_in) * 10
                else:
                    eval_cp = result.score.relative.score(mate_score=10000)
            
            return {
                'move': str(best_move) if best_move else None,
                'evaluation': eval_cp,
                'nodes': getattr(result, 'nodes', 0),
                'time': getattr(result, 'time', 0),
                'success': True
            }
            
    except Exception as e:
        return {
            'move': None,
            'evaluation': None,
            'nodes': 0,
            'time': 0,
            'success': False,
            'error': str(e)
        }

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
            
            # Verify position is valid and has legal moves
            if board.is_valid() and not board.is_game_over() and len(list(board.legal_moves)) > 0:
                positions.append((position_num, board))
            
            position_num += 1
    
    print(f"Loaded {len(positions)} valid positions")
    return positions

def main():
    """Run large-scale engine comparison."""
    print("=== ROBUST LARGE-SCALE ENGINE COMPARISON ===")
    
    # Engine paths
    rubichess_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\RubiChess-avx2\RubiChess.exe"
    stockfish_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
    
    print(f"RubiChess: {rubichess_path}")
    print(f"Stockfish: {stockfish_path}")
    print()
    
    # Load positions
    positions = load_positions_from_pgn('weakness_test_positions.pgn')
    
    # Analysis results
    results = []
    stats = {
        'total': len(positions),
        'rubichess_success': 0,
        'stockfish_success': 0,
        'move_agreement': 0,
        'large_eval_diff': 0
    }
    
    # Analyze each position
    for pos_num, board in positions:
        print(f"[{pos_num}/{len(positions)}] Analyzing position {pos_num}...")
        
        # Analyze with RubiChess
        print("  RubiChess analyzing...")
        rubichess_result = analyze_with_engine(board, rubichess_path, "RubiChess")
        
        if rubichess_result['success']:
            eval_str = f"{rubichess_result['evaluation']:+}cp" if rubichess_result['evaluation'] is not None else "N/A"
            print(f"    RubiChess: {rubichess_result['move']} ({eval_str}) - {rubichess_result['time']:.2f}s")
            stats['rubichess_success'] += 1
        else:
            print(f"    RubiChess: Failed - {rubichess_result.get('error', 'Unknown error')}")
        
        # Analyze with Stockfish
        print("  Stockfish analyzing...")
        stockfish_result = analyze_with_engine(board, stockfish_path, "Stockfish")
        
        if stockfish_result['success']:
            eval_str = f"{stockfish_result['evaluation']:+}cp" if stockfish_result['evaluation'] is not None else "N/A"
            print(f"    Stockfish: {stockfish_result['move']} ({eval_str}) - {stockfish_result['time']:.2f}s")
            stats['stockfish_success'] += 1
        else:
            print(f"    Stockfish: Failed - {stockfish_result.get('error', 'Unknown error')}")
        
        # Compare results
        if rubichess_result['success'] and stockfish_result['success']:
            moves_agree = rubichess_result['move'] == stockfish_result['move']
            if moves_agree:
                stats['move_agreement'] += 1
            
            eval_diff = None
            if (rubichess_result['evaluation'] is not None and 
                stockfish_result['evaluation'] is not None):
                eval_diff = abs(rubichess_result['evaluation'] - stockfish_result['evaluation'])
                if eval_diff > 100:
                    stats['large_eval_diff'] += 1
            
            move_status = "AGREE" if moves_agree else "DIFFER"
            if eval_diff is not None:
                print(f"    Comparison: {eval_diff:.0f}cp difference, moves {move_status}")
            else:
                print(f"    Comparison: moves {move_status}")
        
        # Store result
        result = {
            'position': pos_num,
            'fen': board.fen(),
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
        
        # Save progress every 50 positions
        if pos_num % 50 == 0:
            filename = f"large_scale_progress_{pos_num}.csv"
            print(f"Saving progress to {filename}...")
            
            fieldnames = [
                'position', 'fen',
                'rubichess_move', 'rubichess_eval', 'rubichess_nodes', 'rubichess_time', 'rubichess_success',
                'stockfish_move', 'stockfish_eval', 'stockfish_nodes', 'stockfish_time', 'stockfish_success'
            ]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            # Print statistics
            successful_comparisons = min(stats['rubichess_success'], stats['stockfish_success'])
            print(f"\n=== PROGRESS STATISTICS ===")
            print(f"Positions analyzed: {pos_num}/{stats['total']}")
            print(f"RubiChess success: {stats['rubichess_success']}/{pos_num} ({100*stats['rubichess_success']/pos_num:.1f}%)")
            print(f"Stockfish success: {stats['stockfish_success']}/{pos_num} ({100*stats['stockfish_success']/pos_num:.1f}%)")
            if successful_comparisons > 0:
                print(f"Move agreement: {stats['move_agreement']}/{successful_comparisons} ({100*stats['move_agreement']/successful_comparisons:.1f}%)")
                print(f"Large eval differences (>100cp): {stats['large_eval_diff']}")
            print()
    
    # Final save
    print("Saving final results...")
    fieldnames = [
        'position', 'fen',
        'rubichess_move', 'rubichess_eval', 'rubichess_nodes', 'rubichess_time', 'rubichess_success',
        'stockfish_move', 'stockfish_eval', 'stockfish_nodes', 'stockfish_time', 'stockfish_success'
    ]
    
    with open('large_scale_engine_comparison.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Final statistics
    successful_comparisons = min(stats['rubichess_success'], stats['stockfish_success'])
    print("\n" + "="*60)
    print("LARGE-SCALE ANALYSIS COMPLETE")
    print("="*60)
    print(f"Total positions: {stats['total']}")
    print(f"RubiChess successful analyses: {stats['rubichess_success']}/{stats['total']} ({100*stats['rubichess_success']/stats['total']:.1f}%)")
    print(f"Stockfish successful analyses: {stats['stockfish_success']}/{stats['total']} ({100*stats['stockfish_success']/stats['total']:.1f}%)")
    
    if successful_comparisons > 0:
        print(f"\nComparison Statistics:")
        print(f"Successful comparisons: {successful_comparisons}")
        print(f"Move agreement: {stats['move_agreement']}/{successful_comparisons} ({100*stats['move_agreement']/successful_comparisons:.1f}%)")
        print(f"Positions with >100cp difference: {stats['large_eval_diff']}")
    
    print(f"\nResults saved to large_scale_engine_comparison.csv")
    print("Ready for comprehensive weakness analysis!")

if __name__ == "__main__":
    main()
