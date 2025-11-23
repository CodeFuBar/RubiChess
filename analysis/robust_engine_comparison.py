#!/usr/bin/env python3
"""
Robust engine comparison between RubiChess and Stockfish.
Runs engines separately to avoid crashes and ensures we get benchmark data.
"""

import chess
import chess.pgn
import chess.engine
import csv
import time
import os
from pathlib import Path

# Engine paths
RUBICHESS_PATH = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\RubiChess-avx2\RubiChess.exe"
STOCKFISH_PATH = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"

def load_positions_from_pgn(pgn_file):
    """Load positions from PGN file"""
    positions = []
    try:
        with open(pgn_file, 'r') as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                board = game.board()
                for move in game.mainline_moves():
                    board.push(move)
                
                positions.append({
                    'id': len(positions) + 1,
                    'fen': board.fen()
                })
    except FileNotFoundError:
        print(f"Error: {pgn_file} not found")
        return []
    
    return positions

def analyze_with_engine(engine_path, engine_name, positions, depth=15):
    """Analyze positions with a single engine"""
    print(f"\nAnalyzing {len(positions)} positions with {engine_name}...")
    
    results = []
    
    try:
        # Initialize engine
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        print(f"Engine initialized: {engine.id}")
        
        for i, pos in enumerate(positions, 1):
            print(f"Analyzing position {i}/{len(positions)} with {engine_name}...")
            
            try:
                board = chess.Board(pos['fen'])
                
                # Analyze with time limit as backup
                limit = chess.engine.Limit(depth=depth, time=10.0)
                start_time = time.time()
                
                result = engine.analyse(board, limit)
                
                end_time = time.time()
                analysis_time = end_time - start_time
                
                # Extract results
                best_move = str(result.get('pv', [None])[0]) if result.get('pv') else 'none'
                evaluation = result['score'].relative.score(mate_score=10000) if result.get('score') else 0
                nodes = result.get('nodes', 0)
                depth_reached = result.get('depth', 0)
                
                results.append({
                    'position_id': pos['id'],
                    'fen': pos['fen'],
                    'engine': engine_name,
                    'best_move': best_move,
                    'evaluation_cp': evaluation,
                    'time_taken': analysis_time,
                    'nodes': nodes,
                    'depth_reached': depth_reached
                })
                
                print(f"  {engine_name}: {best_move} ({evaluation}cp) - {analysis_time:.2f}s, {nodes:,} nodes")
                
            except Exception as e:
                print(f"  Error analyzing position {i}: {e}")
                results.append({
                    'position_id': pos['id'],
                    'fen': pos['fen'],
                    'engine': engine_name,
                    'best_move': 'error',
                    'evaluation_cp': 0,
                    'time_taken': 0,
                    'nodes': 0,
                    'depth_reached': 0
                })
        
        # Close engine
        engine.quit()
        
    except Exception as e:
        print(f"Error initializing {engine_name}: {e}")
        return []
    
    return results

def test_engine_connectivity():
    """Test if both engines can be initialized"""
    print("Testing engine connectivity...")
    
    # Test RubiChess
    try:
        engine = chess.engine.SimpleEngine.popen_uci(RUBICHESS_PATH)
        print(f"[OK] RubiChess: {engine.id}")
        engine.quit()
    except Exception as e:
        print(f"[FAIL] RubiChess failed: {e}")
        return False
    
    # Test Stockfish
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        print(f"[OK] Stockfish: {engine.id}")
        engine.quit()
    except Exception as e:
        print(f"[FAIL] Stockfish failed: {e}")
        return False
    
    return True

def main():
    """Main comparison function"""
    print("Robust Engine Comparison: RubiChess vs Stockfish")
    print("=" * 50)
    
    # Test engine connectivity first
    if not test_engine_connectivity():
        print("Engine connectivity test failed. Please check engine paths.")
        return
    
    # Load positions
    positions = load_positions_from_pgn("positions.pgn")
    if not positions:
        print("No positions loaded. Exiting.")
        return
    
    print(f"Loaded {len(positions)} positions for analysis")
    
    # Use smaller subset for initial testing
    test_positions = positions[:20]  # First 20 positions
    print(f"Using {len(test_positions)} positions for comparison")
    
    all_results = []
    
    # Analyze with RubiChess
    rubichess_results = analyze_with_engine(RUBICHESS_PATH, "RubiChess", test_positions)
    all_results.extend(rubichess_results)
    
    # Analyze with Stockfish
    stockfish_results = analyze_with_engine(STOCKFISH_PATH, "Stockfish", test_positions)
    all_results.extend(stockfish_results)
    
    # Save results
    csv_filename = 'engine_comparison_robust.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['position_id', 'fen', 'engine', 'best_move', 'evaluation_cp', 
                     'time_taken', 'nodes', 'depth_reached']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in all_results:
            writer.writerow(result)
    
    print(f"\nResults saved to {csv_filename}")
    
    # Summary statistics
    rubichess_count = len([r for r in all_results if r['engine'] == 'RubiChess' and r['evaluation_cp'] != 0])
    stockfish_count = len([r for r in all_results if r['engine'] == 'Stockfish' and r['evaluation_cp'] != 0])
    
    print(f"Successful RubiChess analyses: {rubichess_count}")
    print(f"Successful Stockfish analyses: {stockfish_count}")
    
    if rubichess_count > 0 and stockfish_count > 0:
        print("\n[SUCCESS] Both engines provided results - ready for comparison analysis!")
        
        # Quick comparison preview
        print("\nSample comparisons:")
        for pos_id in range(1, min(6, len(test_positions) + 1)):
            rubi_result = next((r for r in all_results if r['position_id'] == pos_id and r['engine'] == 'RubiChess'), None)
            stock_result = next((r for r in all_results if r['position_id'] == pos_id and r['engine'] == 'Stockfish'), None)
            
            if rubi_result and stock_result:
                eval_diff = abs(rubi_result['evaluation_cp'] - stock_result['evaluation_cp'])
                print(f"Position {pos_id}: RubiChess {rubi_result['evaluation_cp']}cp vs Stockfish {stock_result['evaluation_cp']}cp (diff: {eval_diff}cp)")
    
    return all_results

if __name__ == "__main__":
    main()
