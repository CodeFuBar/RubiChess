#!/usr/bin/env python3
"""
Run engine comparisons between RubiChess and Stockfish on test positions.
Uses direct UCI communication instead of cutechess-cli for better control.
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

# Alternative Stockfish paths to try
STOCKFISH_ALTERNATIVES = [
    r"C:\Program Files\Stockfish\stockfish.exe",
    r"C:\Users\Public\Documents\ChessBase\Engines\stockfish.exe",
    r"stockfish.exe"  # If in PATH
]

def find_stockfish():
    """Find Stockfish executable"""
    if os.path.exists(STOCKFISH_PATH):
        return STOCKFISH_PATH
    
    for path in STOCKFISH_ALTERNATIVES:
        if os.path.exists(path):
            return path
    
    # Try to find stockfish in common locations
    common_paths = [
        r"C:\Program Files\Stockfish",
        r"C:\Program Files (x86)\Stockfish",
        r"C:\Users\Public\Documents\ChessBase\Engines"
    ]
    
    for base_path in common_paths:
        if os.path.exists(base_path):
            for file in os.listdir(base_path):
                if "stockfish" in file.lower() and file.endswith(".exe"):
                    return os.path.join(base_path, file)
    
    return None

def analyze_position(engine, board, depth=15, time_limit=5.0):
    """Analyze a position with given engine"""
    try:
        start_time = time.time()
        
        # Analyze with depth limit and time limit
        info = engine.analyse(board, chess.engine.Limit(depth=depth, time=time_limit))
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        # Extract evaluation
        score = info.get("score")
        if score:
            if score.is_mate():
                # Convert mate score to centipawns (mate in N = +/- (10000 - N*10))
                mate_in = score.mate()
                if mate_in > 0:
                    eval_cp = 10000 - mate_in * 10
                else:
                    eval_cp = -10000 - mate_in * 10
            else:
                eval_cp = score.relative.score(mate_score=10000)
        else:
            eval_cp = 0
        
        # Get best move
        best_move = info.get("pv", [None])[0]
        best_move_str = str(best_move) if best_move else "none"
        
        # Get nodes searched
        nodes = info.get("nodes", 0)
        
        return {
            "best_move": best_move_str,
            "evaluation_cp": eval_cp,
            "time_taken": analysis_time,
            "nodes": nodes,
            "depth": info.get("depth", 0)
        }
        
    except Exception as e:
        print(f"Error analyzing position: {e}")
        return {
            "best_move": "error",
            "evaluation_cp": 0,
            "time_taken": 0,
            "nodes": 0,
            "depth": 0
        }

def load_positions_from_pgn(filename):
    """Load positions from PGN file"""
    positions = []
    
    with open(filename, "r") as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            
            # Get the position from FEN header or starting position
            if "FEN" in game.headers:
                fen = game.headers["FEN"]
            else:
                fen = chess.STARTING_FEN
            
            positions.append({
                "round": game.headers.get("Round", ""),
                "fen": fen,
                "description": f"Position {len(positions) + 1}"
            })
    
    return positions

def main():
    """Run engine comparison on all test positions"""
    print("Starting engine comparison analysis...")
    
    # Check if engines exist
    if not os.path.exists(RUBICHESS_PATH):
        print(f"Error: RubiChess not found at {RUBICHESS_PATH}")
        return
    
    stockfish_path = find_stockfish()
    if not stockfish_path:
        print("Error: Stockfish not found. Please install Stockfish or update the path.")
        return
    
    print(f"Using RubiChess: {RUBICHESS_PATH}")
    print(f"Using Stockfish: {stockfish_path}")
    
    # Load test positions
    positions = load_positions_from_pgn("positions.pgn")
    print(f"Loaded {len(positions)} positions for analysis")
    
    # Prepare CSV output
    csv_filename = "engine_comparison.csv"
    csv_headers = [
        "position_id", "fen", "engine", "best_move", "evaluation_cp", 
        "time_taken", "nodes", "depth_reached"
    ]
    
    results = []
    
    # Initialize engines
    try:
        print("Initializing engines...")
        rubichess = chess.engine.SimpleEngine.popen_uci(RUBICHESS_PATH)
        stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        
        print("Engines initialized successfully!")
        
        # Analyze each position with both engines
        for i, pos_data in enumerate(positions, 1):
            fen = pos_data["fen"]
            print(f"\nAnalyzing position {i}/{len(positions)}: {fen[:50]}...")
            
            try:
                board = chess.Board(fen)
                
                # Analyze with RubiChess
                print("  RubiChess analyzing...")
                rubichess_result = analyze_position(rubichess, board, depth=15, time_limit=5.0)
                results.append({
                    "position_id": i,
                    "fen": fen,
                    "engine": "RubiChess",
                    **rubichess_result
                })
                
                # Analyze with Stockfish
                print("  Stockfish analyzing...")
                stockfish_result = analyze_position(stockfish, board, depth=15, time_limit=5.0)
                results.append({
                    "position_id": i,
                    "fen": fen,
                    "engine": "Stockfish",
                    **stockfish_result
                })
                
                print(f"  RubiChess: {rubichess_result['best_move']} ({rubichess_result['evaluation_cp']}cp)")
                print(f"  Stockfish: {stockfish_result['best_move']} ({stockfish_result['evaluation_cp']}cp)")
                
            except Exception as e:
                print(f"  Error with position {i}: {e}")
                continue
        
        # Close engines
        rubichess.quit()
        stockfish.quit()
        
    except Exception as e:
        print(f"Error initializing engines: {e}")
        return
    
    # Save results to CSV even if incomplete
    csv_filename = 'engine_comparison.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['position_id', 'fen', 'engine', 'best_move', 'evaluation_cp', 
                     'time_taken', 'nodes', 'depth_reached']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow(result)
    
    print(f"\nResults saved to {csv_filename}")
    print(f"Total comparisons: {len(results)}")
    
    # Summary statistics
    rubichess_results = [r for r in results if r['engine'] == 'RubiChess']
    stockfish_results = [r for r in results if r['engine'] == 'Stockfish']
    
    print(f"RubiChess results: {len(rubichess_results)}")
    print(f"Stockfish results: {len(stockfish_results)}")
    
    if rubichess_results:
        avg_time_rubi = sum(r['time_taken'] for r in rubichess_results if r['time_taken'] > 0) / len([r for r in rubichess_results if r['time_taken'] > 0])
        avg_eval_rubi = sum(r['evaluation_cp'] for r in rubichess_results if r['evaluation_cp'] != 0) / len([r for r in rubichess_results if r['evaluation_cp'] != 0])
        print(f"RubiChess average time: {avg_time_rubi:.2f}s")
        print(f"RubiChess average evaluation: {avg_eval_rubi:.1f}cp")
    
    if stockfish_results:
        valid_stockfish = [r for r in stockfish_results if r['time_taken'] > 0]
        if valid_stockfish:
            avg_time_stock = sum(r['time_taken'] for r in valid_stockfish) / len(valid_stockfish)
            print(f"Stockfish average time: {avg_time_stock:.2f}s")
        else:
            print("Stockfish: No valid results (engine crashed)")
    
    print(f"Analyzed {len(results)//2} positions with both engines")

if __name__ == "__main__":
    main()
