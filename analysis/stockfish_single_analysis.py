#!/usr/bin/env python3
"""
Single position analysis with Stockfish to avoid crashes.
Restart engine for each position to prevent accumulated errors.
"""

import chess
import chess.pgn
import chess.engine
import csv
import time
import subprocess
import os

# Engine paths
STOCKFISH_PATH = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"

def load_positions_from_pgn(pgn_file, max_positions=20):
    """Load positions from PGN file"""
    positions = []
    try:
        with open(pgn_file, 'r') as f:
            count = 0
            while count < max_positions:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                board = game.board()
                for move in game.mainline_moves():
                    board.push(move)
                
                positions.append({
                    'id': count + 1,
                    'fen': board.fen()
                })
                count += 1
    except FileNotFoundError:
        print(f"Error: {pgn_file} not found")
        return []
    
    return positions

def analyze_single_position_stockfish(fen, position_id, depth=15):
    """Analyze single position with fresh Stockfish instance"""
    try:
        # Create fresh engine instance
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        
        board = chess.Board(fen)
        limit = chess.engine.Limit(depth=depth, time=8.0)
        
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
            'engine': 'Stockfish',
            'best_move': best_move,
            'evaluation_cp': evaluation,
            'time_taken': analysis_time,
            'nodes': nodes,
            'depth_reached': depth_reached,
            'success': True
        }
        
    except Exception as e:
        print(f"  Error analyzing position {position_id}: {e}")
        return {
            'position_id': position_id,
            'fen': fen,
            'engine': 'Stockfish',
            'best_move': 'error',
            'evaluation_cp': 0,
            'time_taken': 0,
            'nodes': 0,
            'depth_reached': 0,
            'success': False
        }

def main():
    """Main function to analyze positions with Stockfish"""
    print("Stockfish Single Position Analysis")
    print("=" * 40)
    
    # Load positions
    positions = load_positions_from_pgn("positions.pgn", max_positions=20)
    if not positions:
        print("No positions loaded. Exiting.")
        return
    
    print(f"Analyzing {len(positions)} positions with Stockfish...")
    
    stockfish_results = []
    
    for pos in positions:
        print(f"Analyzing position {pos['id']}/20 with Stockfish...")
        
        result = analyze_single_position_stockfish(pos['fen'], pos['id'])
        stockfish_results.append(result)
        
        if result['success']:
            print(f"  Stockfish: {result['best_move']} ({result['evaluation_cp']}cp) - {result['time_taken']:.2f}s, {result['nodes']:,} nodes")
        else:
            print(f"  Stockfish: Failed to analyze position {pos['id']}")
        
        # Small delay between analyses
        time.sleep(0.5)
    
    # Load existing RubiChess results
    rubichess_results = []
    try:
        with open('engine_comparison_robust.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['engine'] == 'RubiChess':
                    rubichess_results.append({
                        'position_id': int(row['position_id']),
                        'fen': row['fen'],
                        'engine': row['engine'],
                        'best_move': row['best_move'],
                        'evaluation_cp': int(row['evaluation_cp']),
                        'time_taken': float(row['time_taken']),
                        'nodes': int(row['nodes']),
                        'depth_reached': int(row['depth_reached'])
                    })
    except FileNotFoundError:
        print("Warning: No existing RubiChess results found")
    
    # Combine results
    all_results = rubichess_results + [r for r in stockfish_results if r['success']]
    
    # Save combined results
    csv_filename = 'engine_comparison_complete.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['position_id', 'fen', 'engine', 'best_move', 'evaluation_cp', 
                     'time_taken', 'nodes', 'depth_reached']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in all_results:
            # Remove 'success' field for CSV output
            csv_row = {k: v for k, v in result.items() if k != 'success'}
            writer.writerow(csv_row)
    
    print(f"\nResults saved to {csv_filename}")
    
    # Summary
    successful_stockfish = len([r for r in stockfish_results if r['success']])
    print(f"Successful Stockfish analyses: {successful_stockfish}/20")
    print(f"RubiChess analyses: {len(rubichess_results)}")
    
    if successful_stockfish > 0 and len(rubichess_results) > 0:
        print("\n[SUCCESS] Both engines have results - ready for comparison!")
        
        # Quick comparison preview
        print("\nSample comparisons:")
        for pos_id in range(1, min(6, successful_stockfish + 1)):
            rubi_result = next((r for r in rubichess_results if r['position_id'] == pos_id), None)
            stock_result = next((r for r in stockfish_results if r['position_id'] == pos_id and r['success']), None)
            
            if rubi_result and stock_result:
                eval_diff = abs(rubi_result['evaluation_cp'] - stock_result['evaluation_cp'])
                print(f"Position {pos_id}: RubiChess {rubi_result['evaluation_cp']}cp vs Stockfish {stock_result['evaluation_cp']}cp (diff: {eval_diff}cp)")

if __name__ == "__main__":
    main()
