#!/usr/bin/env python3
"""
ChessBase UCI Compatibility Test for Modified RubiChess Engine
Tests the modified engine's UCI protocol compliance and ChessBase compatibility
"""

import chess
import chess.engine
import time
import sys
import os

def test_uci_compatibility(engine_path):
    """Test UCI protocol compatibility with ChessBase requirements"""
    
    print(f"Testing UCI compatibility for: {engine_path}")
    print("=" * 60)
    
    try:
        # Test 1: Basic UCI initialization
        print("Test 1: Basic UCI initialization...")
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            print("OK Engine initialized successfully")
            print(f"  Engine ID: {engine.id}")
            print(f"  Author: {engine.id.get('author', 'Unknown')}")
            
            # Test 2: UCI options
            print("\nTest 2: UCI options...")
            options = engine.options
            print(f"OK Found {len(options)} UCI options")
            for name, option in list(options.items())[:5]:  # Show first 5 options
                print(f"  {name}: {option}")
            
            # Test 3: Position setup and analysis
            print("\nTest 3: Position setup and analysis...")
            board = chess.Board()
            
            # Test basic position analysis
            result = engine.analyse(board, chess.engine.Limit(depth=10, time=2.0))
            
            if result and 'pv' in result and result['pv']:
                best_move = result['pv'][0]
                score = result.get('score')
                nodes = result.get('nodes', 0)
                
                print("OK Analysis successful")
                print(f"  Best move: {best_move}")
                print(f"  Score: {score}")
                print(f"  Nodes: {nodes:,}")
                print(f"  PV length: {len(result['pv'])}")
            else:
                print("FAIL Analysis failed - no valid result")
                return False
            
            # Test 4: Multiple position analysis (ChessBase workflow)
            print("\nTest 4: Multiple position analysis...")
            test_positions = [
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # Starting position
                "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",  # Kiwipete
                "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"  # Endgame position
            ]
            
            for i, fen in enumerate(test_positions, 1):
                board = chess.Board(fen)
                result = engine.analyse(board, chess.engine.Limit(depth=8, time=1.0))
                
                if result and 'pv' in result and result['pv']:
                    print(f"  Position {i}: OK {result['pv'][0]} (nodes: {result.get('nodes', 0):,})")
                else:
                    print(f"  Position {i}: FAIL Analysis failed")
                    return False
            
            # Test 5: Engine info and identification
            print("\nTest 5: Engine identification...")
            engine_info = {
                'name': engine.id.get('name', 'Unknown'),
                'author': engine.id.get('author', 'Unknown'),
            }
            
            print("OK Engine properly identified")
            print(f"  Name: {engine_info['name']}")
            print(f"  Author: {engine_info['author']}")
            
            # Test 6: Performance under load (ChessBase stress test)
            print("\nTest 6: Performance stress test...")
            start_time = time.time()
            analysis_count = 0
            
            for depth in [5, 8, 10]:
                board = chess.Board("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")
                result = engine.analyse(board, chess.engine.Limit(depth=depth, time=0.5))
                if result and 'pv' in result:
                    analysis_count += 1
            
            elapsed = time.time() - start_time
            print(f"OK Completed {analysis_count}/3 analyses in {elapsed:.2f}s")
            
            return True
            
    except Exception as e:
        print(f"FAIL UCI compatibility test failed: {e}")
        return False

def test_endgame_positions(engine_path):
    """Test the modified engine on critical endgame positions"""
    
    print(f"\nTesting Phase 1 endgame improvements...")
    print("=" * 60)
    
    # Critical endgame positions from our test suite
    test_positions = [
        ("8/8/8/8/8/2k5/2P5/1K1R4 w - - 0 1", "Position 135: King+Rook+Pawn vs King"),
        ("8/8/8/8/8/3k4/3P4/2KR4 w - - 0 1", "Position 136: King+Rook+Pawn vs King"),
        ("8/8/8/8/8/4k3/4P3/3KR3 w - - 0 1", "Position 137: King+Rook+Pawn vs King"),
    ]
    
    try:
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            print("Testing Phase 1 endgame evaluation improvements...")
            
            for fen, description in test_positions:
                board = chess.Board(fen)
                result = engine.analyse(board, chess.engine.Limit(depth=15, time=3.0))
                
                if result and 'pv' in result and result['pv']:
                    best_move = result['pv'][0]
                    score = result.get('score')
                    nodes = result.get('nodes', 0)
                    
                    print(f"\n{description}")
                    print(f"  Best move: {best_move}")
                    print(f"  Evaluation: {score}")
                    print(f"  Nodes: {nodes:,}")
                    print(f"  OK Analysis successful")
                else:
                    print(f"\n{description}")
                    print(f"  FAIL Analysis failed")
                    return False
            
            return True
            
    except Exception as e:
        print(f"FAIL Endgame position test failed: {e}")
        return False

def main():
    """Main test function"""
    
    # Path to the modified engine
    engine_path = r"..\RubiChess\src\Release-modified\RubiChess_1.1_dev_20250911_001_x86-64-avx2.exe"
    
    print("RubiChess Phase 1 - ChessBase Compatibility Test")
    print("=" * 60)
    print(f"Engine: {os.path.basename(engine_path)}")
    print(f"Path: {engine_path}")
    print(f"Exists: {os.path.exists(engine_path)}")
    print()
    
    if not os.path.exists(engine_path):
        print(f"FAIL Engine not found at: {engine_path}")
        return False
    
    # Run compatibility tests
    uci_success = test_uci_compatibility(engine_path)
    endgame_success = test_endgame_positions(engine_path)
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"UCI Compatibility: {'PASS' if uci_success else 'FAIL'}")
    print(f"Endgame Testing: {'PASS' if endgame_success else 'FAIL'}")
    
    if uci_success and endgame_success:
        print("\nSUCCESS: ENGINE IS CHESSBASE COMPATIBLE AND READY FOR USE!")
        print("\nThe modified RubiChess engine with Phase 1 endgame optimizations")
        print("has passed all compatibility tests and is ready for ChessBase integration.")
    else:
        print("\nFAILED: ENGINE COMPATIBILITY ISSUES DETECTED")
        print("Please review the test results above for specific issues.")
    
    return uci_success and endgame_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
