#!/usr/bin/env python3
"""
Compare NNUE networks for RubiChess evaluation accuracy.
Tests against Stockfish as reference.
"""
import subprocess
import os
import time

# Paths
RUBICHESS_PATH = r"D:\Windsurf\RubiChessAdvanced\RubiChess\src\Release-optimal\RubiChess_avx512_pgo.exe"
RUBICHESS_DIR = os.path.dirname(RUBICHESS_PATH)
STOCKFISH_PATH = r"D:\Windsurf\RubiChessAdvanced\ChessEngineTestFramework\engines\stockfish_25090605_x64_avx2.exe"

# Networks to test
NETWORKS = [
    ("June 2023 (current)", "nn-d901a1822f-20230606.nnue"),
    ("May 2025", "nn-f05142b28f-20250520.nnue"),
    ("Oct 2025 (newest)", "nn-be4dcd7c83-20251031.nnue"),
]

# Test positions with Stockfish reference evaluations
TEST_POSITIONS = [
    # Opening positions
    ("Starting position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
    ("Sicilian Defense", "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"),
    ("Queen's Gambit", "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2"),
    
    # Middlegame tactical
    ("Kiwipete", "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"),
    ("Tactical 1", "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"),
    ("Complex middlegame", "r1bq1rk1/pp2ppbp/2np1np1/8/2BNP3/2N1B3/PPP2PPP/R2QK2R w KQ - 0 9"),
    
    # Endgame positions
    ("Rook endgame", "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"),
    ("Pawn endgame", "8/8/4k3/8/2p5/8/B2K4/8 w - - 0 1"),
    ("Rook vs pawns", "6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1"),
    
    # Imbalanced positions
    ("Queen vs pieces", "r1b2rk1/pp3ppp/2n1pn2/q7/1bBP4/2N1PN2/PP3PPP/R1BQ1RK1 w - - 0 10"),
    ("Bishops pair", "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"),
]

def get_stockfish_eval(fen, depth=16):
    """Get Stockfish evaluation for a position"""
    try:
        process = subprocess.Popen(
            [STOCKFISH_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        commands = f"uci\nisready\nposition fen {fen}\ngo depth {depth}\n"
        process.stdin.write(commands)
        process.stdin.flush()
        
        eval_cp = None
        start = time.time()
        while time.time() - start < 30:
            line = process.stdout.readline()
            if "score cp" in line:
                parts = line.split("score cp")
                if len(parts) > 1:
                    eval_cp = int(parts[1].split()[0])
            elif "score mate" in line:
                parts = line.split("score mate")
                if len(parts) > 1:
                    mate_in = int(parts[1].split()[0])
                    eval_cp = 10000 if mate_in > 0 else -10000
            elif "bestmove" in line:
                break
        
        process.stdin.write("quit\n")
        process.stdin.flush()
        process.wait(timeout=2)
        
        return eval_cp
    except Exception as e:
        print(f"Stockfish error: {e}")
        return None

def get_rubichess_eval(fen, network_path, depth=14):
    """Get RubiChess evaluation with specific network"""
    try:
        # Copy network to engine directory
        src_network = os.path.join(r"D:\Windsurf\RubiChessAdvanced\RubiChess\src", network_path)
        
        process = subprocess.Popen(
            [RUBICHESS_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=RUBICHESS_DIR,
            bufsize=1
        )
        
        # Set network path
        commands = f"uci\nsetoption name NNUENetpath value {src_network}\nisready\nposition fen {fen}\ngo depth {depth}\n"
        process.stdin.write(commands)
        process.stdin.flush()
        
        eval_cp = None
        start = time.time()
        while time.time() - start < 60:
            line = process.stdout.readline()
            if "score cp" in line:
                parts = line.split("score cp")
                if len(parts) > 1:
                    eval_cp = int(parts[1].split()[0])
            elif "score mate" in line:
                parts = line.split("score mate")
                if len(parts) > 1:
                    mate_in = int(parts[1].split()[0])
                    eval_cp = 10000 if mate_in > 0 else -10000
            elif "bestmove" in line:
                break
        
        process.stdin.write("quit\n")
        process.stdin.flush()
        try:
            process.wait(timeout=2)
        except:
            process.kill()
        
        return eval_cp
    except Exception as e:
        print(f"RubiChess error: {e}")
        return None

def main():
    print("="*80)
    print("NNUE NETWORK COMPARISON TEST")
    print("="*80)
    print(f"\nReference: Stockfish (depth 16)")
    print(f"Test engine: RubiChess+ (depth 14)")
    print(f"Positions: {len(TEST_POSITIONS)}")
    print()
    
    # Get Stockfish evaluations first
    print("Getting Stockfish reference evaluations...")
    sf_evals = {}
    for name, fen in TEST_POSITIONS:
        eval_cp = get_stockfish_eval(fen)
        sf_evals[fen] = eval_cp
        print(f"  {name}: {eval_cp} cp")
    print()
    
    # Test each network
    results = {}
    for net_name, net_file in NETWORKS:
        print(f"\n{'='*80}")
        print(f"Testing: {net_name}")
        print(f"Network: {net_file}")
        print("="*80)
        
        total_diff = 0
        count = 0
        position_results = []
        
        for pos_name, fen in TEST_POSITIONS:
            rubi_eval = get_rubichess_eval(fen, net_file)
            sf_eval = sf_evals.get(fen)
            
            if rubi_eval is not None and sf_eval is not None:
                diff = abs(rubi_eval - sf_eval)
                total_diff += diff
                count += 1
                position_results.append((pos_name, sf_eval, rubi_eval, diff))
                print(f"  {pos_name}: SF={sf_eval:+d} Rubi={rubi_eval:+d} Diff={diff}")
            else:
                print(f"  {pos_name}: ERROR")
        
        avg_diff = total_diff / count if count > 0 else 0
        results[net_name] = {
            'avg_diff': avg_diff,
            'total_diff': total_diff,
            'count': count,
            'positions': position_results
        }
        print(f"\n  Average difference: {avg_diff:.1f} cp")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n{'Network':<25} {'Avg Diff (cp)':<15} {'Total Diff':<15}")
    print("-"*60)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_diff'])
    for net_name, data in sorted_results:
        print(f"{net_name:<25} {data['avg_diff']:<15.1f} {data['total_diff']:<15.0f}")
    
    best = sorted_results[0]
    print(f"\n[BEST] {best[0]} with average difference of {best[1]['avg_diff']:.1f} cp")
    
    # Recommendation
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    if best[0] != "June 2023 (current)":
        print(f"\nSwitch to {best[0]} for better evaluation accuracy.")
    else:
        print(f"\nKeep current network - it has the best evaluation accuracy.")

if __name__ == "__main__":
    main()
