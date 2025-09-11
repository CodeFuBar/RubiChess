#!/usr/bin/env python3
"""
Debug script to check test components
"""

import chess
import chess.pgn
import chess.engine
from pathlib import Path

def check_pgn_positions():
    """Check if we can load positions from PGN"""
    try:
        with open('comprehensive_positions.pgn', 'r') as f:
            game_count = 0
            positions_135_142 = []
            
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                game_count += 1
                if 135 <= game_count <= 142:
                    positions_135_142.append((game_count, game.headers.get('Event', 'Unknown')))
                
                if game_count > 142:
                    break
            
            print(f"Total games scanned: {game_count}")
            print(f"Positions 135-142 found: {len(positions_135_142)}")
            for pos_id, event in positions_135_142:
                print(f"  Position {pos_id}: {event}")
            
            return len(positions_135_142) > 0
            
    except Exception as e:
        print(f"Error reading PGN: {e}")
        return False

def check_engines():
    """Check if engines are accessible"""
    engines = {
        'Original RubiChess': r"d:\Windsurf\RubiChessAdvanced\RubiChess\x64\Release\RubiChess.exe",
        'Modified RubiChess': r"d:\Windsurf\RubiChessAdvanced\RubiChess\src\Release-modified\RubiChess_1.1_dev_20250911_001_x86-64-avx2.exe",
        'Stockfish': r"C:\Users\Andreas\AppData\Local\ChessBase\Engines\stockfish_15_win_x64_avx2.exe"
    }
    
    for name, path in engines.items():
        exists = Path(path).exists()
        print(f"{name}: {'OK' if exists else 'MISSING'} ({path})")
        
        if exists:
            try:
                # Quick UCI test
                with chess.engine.SimpleEngine.popen_uci(path) as engine:
                    print(f"  UCI connection: OK")
            except Exception as e:
                print(f"  UCI connection: ERROR ({e})")

def test_simple_analysis():
    """Test a simple position analysis"""
    # Simple starting position
    board = chess.Board()
    
    modified_engine = r"d:\Windsurf\RubiChessAdvanced\RubiChess\src\Release-modified\RubiChess_1.1_dev_20250911_001_x86-64-avx2.exe"
    
    if Path(modified_engine).exists():
        try:
            print("Testing modified engine on starting position...")
            with chess.engine.SimpleEngine.popen_uci(modified_engine) as engine:
                result = engine.analyse(board, chess.engine.Limit(depth=10, time=3.0))
                print(f"  Analysis successful: {result}")
                return True
        except Exception as e:
            print(f"  Analysis failed: {e}")
            return False
    else:
        print("Modified engine not found!")
        return False

if __name__ == "__main__":
    print("=== Debug Test Components ===")
    print()
    
    print("1. Checking PGN positions...")
    pgn_ok = check_pgn_positions()
    print()
    
    print("2. Checking engine accessibility...")
    check_engines()
    print()
    
    print("3. Testing simple analysis...")
    analysis_ok = test_simple_analysis()
    print()
    
    print(f"PGN: {'OK' if pgn_ok else 'ERROR'}")
    print(f"Analysis: {'OK' if analysis_ok else 'ERROR'}")
