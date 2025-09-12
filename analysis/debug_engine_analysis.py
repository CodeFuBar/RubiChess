#!/usr/bin/env python3
"""
Debug engine analysis to identify the issue.
"""

import chess
import chess.engine
import traceback

def debug_engine_analysis():
    """Debug engine analysis to see what's going wrong."""
    
    # Test position
    board = chess.Board("7R/8/8/8/8/3k4/3p4/3K4 b - - 1 1")
    
    # Engine paths
    rubichess_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\RubiChess-avx2\RubiChess.exe"
    stockfish_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
    
    print("Testing RubiChess engine analysis...")
    try:
        with chess.engine.SimpleEngine.popen_uci(rubichess_path) as engine:
            print(f"Engine connected: {engine}")
            
            # Try basic analysis
            result = engine.analyse(board, chess.engine.Limit(depth=10, time=5.0))
            print(f"Analysis result type: {type(result)}")
            print(f"Analysis result: {result}")
            
            # Check attributes
            print(f"Has pv attribute: {hasattr(result, 'pv')}")
            print(f"Has score attribute: {hasattr(result, 'score')}")
            
            if hasattr(result, 'pv'):
                print(f"PV: {result.pv}")
                print(f"PV type: {type(result.pv)}")
            
            if hasattr(result, 'score'):
                print(f"Score: {result.score}")
                print(f"Score type: {type(result.score)}")
                
            # Try to extract move
            if hasattr(result, 'pv') and result.pv:
                best_move = result.pv[0]
                print(f"Best move: {best_move}")
            
    except Exception as e:
        print(f"RubiChess analysis failed: {e}")
        traceback.print_exc()
    
    print("\nTesting Stockfish engine analysis...")
    try:
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            print(f"Engine connected: {engine}")
            
            # Try basic analysis
            result = engine.analyse(board, chess.engine.Limit(depth=10, time=5.0))
            print(f"Analysis result type: {type(result)}")
            print(f"Analysis result: {result}")
            
            # Check attributes
            print(f"Has pv attribute: {hasattr(result, 'pv')}")
            print(f"Has score attribute: {hasattr(result, 'score')}")
            
            if hasattr(result, 'pv'):
                print(f"PV: {result.pv}")
                print(f"PV type: {type(result.pv)}")
            
            if hasattr(result, 'score'):
                print(f"Score: {result.score}")
                print(f"Score type: {type(result.score)}")
                
            # Try to extract move
            if hasattr(result, 'pv') and result.pv:
                best_move = result.pv[0]
                print(f"Best move: {best_move}")
            
    except Exception as e:
        print(f"Stockfish analysis failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_engine_analysis()
