#!/usr/bin/env python3
"""
Comprehensive engine comparison between RubiChess and Stockfish on 126+ positions.
Handles engine crashes gracefully and provides detailed progress tracking.
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
        depth_reached = result.get('depth', 0)
        
        # Close engine immediately
        engine.quit()
        
        return {
            'position_id': position_id,
            'fen': fen,
            'engine': engine_name,
            'best_move': best_move,
            'evaluation_cp': evaluation,
            'time_taken': analysis_time,
            'nodes': nodes,
            'depth_reached': depth_reached,
            'success': True
        }
        
    except Exception as e:
        print(f"    Error: {e}")
        return {
            'position_id': position_id,
            'fen': fen,
            'engine': engine_name,
            'best_move': 'error',
            'evaluation_cp': 0,
            'time_taken': 0,
            'nodes': 0,
            'depth_reached': 0,
            'success': False
        }

def save_progress(results, filename):
    """Save current results to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['position_id', 'fen', 'engine', 'best_move', 'evaluation_cp', 
                     'time_taken', 'nodes', 'depth_reached']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            if result['success']:
                csv_row = {k: v for k, v in result.items() if k != 'success'}
                writer.writerow(csv_row)

def main():
    """Main comprehensive comparison function"""
    print("Comprehensive Engine Comparison: RubiChess vs Stockfish")
    print("=" * 60)
    
    # Load positions
    positions = load_positions_from_pgn("comprehensive_positions.pgn")
    if not positions:
        print("No positions loaded. Exiting.")
        return
    
    print(f"Loaded {len(positions)} positions for comprehensive analysis")
    
    all_results = []
    rubichess_success = 0
    stockfish_success = 0
    
    # Process each position
    for i, pos in enumerate(positions, 1):
        print(f"\n[{i}/{len(positions)}] Analyzing position {pos['id']}...")
        
        # Analyze with RubiChess
        print(f"  RubiChess analyzing...")
        rubi_result = analyze_single_position(RUBICHESS_PATH, "RubiChess", pos['fen'], pos['id'])
        all_results.append(rubi_result)
        
        if rubi_result['success']:
            rubichess_success += 1
            print(f"    RubiChess: {rubi_result['best_move']} ({rubi_result['evaluation_cp']:+}cp) - {rubi_result['time_taken']:.2f}s")
        else:
            print(f"    RubiChess: Failed")
        
        # Small delay between engines
        time.sleep(0.2)
        
        # Analyze with Stockfish
        print(f"  Stockfish analyzing...")
        stock_result = analyze_single_position(STOCKFISH_PATH, "Stockfish", pos['fen'], pos['id'])
        all_results.append(stock_result)
        
        if stock_result['success']:
            stockfish_success += 1
            print(f"    Stockfish: {stock_result['best_move']} ({stock_result['evaluation_cp']:+}cp) - {stock_result['time_taken']:.2f}s")
        else:
            print(f"    Stockfish: Failed")
        
        # Show comparison if both succeeded
        if rubi_result['success'] and stock_result['success']:
            eval_diff = abs(rubi_result['evaluation_cp'] - stock_result['evaluation_cp'])
            move_agree = rubi_result['best_move'] == stock_result['best_move']
            agree_str = "AGREE" if move_agree else "DIFFER"
            print(f"    Comparison: {eval_diff}cp difference, moves {agree_str}")
        
        # Save progress every 10 positions
        if i % 10 == 0:
            save_progress(all_results, f'comprehensive_progress_{i}.csv')
            print(f"  Progress saved (RubiChess: {rubichess_success}/{i}, Stockfish: {stockfish_success}/{i})")
        
        # Small delay between positions
        time.sleep(0.3)
    
    # Save final results
    csv_filename = 'comprehensive_engine_comparison.csv'
    save_progress(all_results, csv_filename)
    
    print(f"\n" + "=" * 60)
    print(f"COMPREHENSIVE ANALYSIS COMPLETE")
    print(f"=" * 60)
    print(f"Total positions: {len(positions)}")
    print(f"RubiChess successful analyses: {rubichess_success}/{len(positions)} ({rubichess_success/len(positions)*100:.1f}%)")
    print(f"Stockfish successful analyses: {stockfish_success}/{len(positions)} ({stockfish_success/len(positions)*100:.1f}%)")
    
    # Calculate comparison statistics
    successful_comparisons = 0
    move_agreements = 0
    eval_differences = []
    
    for i in range(0, len(all_results), 2):
        if i + 1 < len(all_results):
            rubi_result = all_results[i]
            stock_result = all_results[i + 1]
            
            if rubi_result['success'] and stock_result['success']:
                successful_comparisons += 1
                
                if rubi_result['best_move'] == stock_result['best_move']:
                    move_agreements += 1
                
                eval_diff = abs(rubi_result['evaluation_cp'] - stock_result['evaluation_cp'])
                eval_differences.append(eval_diff)
    
    if successful_comparisons > 0:
        print(f"\nComparison Statistics:")
        print(f"Successful comparisons: {successful_comparisons}")
        print(f"Move agreement: {move_agreements}/{successful_comparisons} ({move_agreements/successful_comparisons*100:.1f}%)")
        print(f"Mean absolute evaluation difference: {sum(eval_differences)/len(eval_differences):.1f}cp")
        print(f"Max evaluation difference: {max(eval_differences):.1f}cp")
        
        large_differences = [d for d in eval_differences if d > 100]
        print(f"Positions with >100cp difference: {len(large_differences)}")
    
    print(f"\nResults saved to {csv_filename}")
    print("Ready for comprehensive analysis!")

if __name__ == "__main__":
    main()
