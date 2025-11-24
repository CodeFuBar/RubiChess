#!/usr/bin/env python3
"""
Compare original RubiChess vs modified (Phase 1) RubiChess evaluations
"""
import subprocess
import os
import time
import re

# Binaries to test
binaries = {
    "Modified (Phase 1)": r"D:\Windsurf\RubiChessAdvanced\RubiChess\x64\Release\RubiChess.exe",
    "Original": r"D:\Windsurf\RubiChessAdvanced\RubiChess\src\Release-modified\RubiChess_1.1_dev_20250911_001_x86-64-avx2.exe",
}

# Test positions
positions = {
    60: ("Opening", "r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/3PbN2/PPP2PPP/RNBQ1RK1 w kq - 1 6"),
    98: ("Pawn EG (Black)", "8/8/2k5/5p2/6p1/2K5/3P4/8 b - - 1 1"),
    103: ("Pawn EG (Black)", "8/8/1p1k4/3p4/3P4/1P6/4K3/8 b - - 1 1"),
}

def get_evaluation(binary_path, fen, depth=12):
    """Run search and extract evaluation"""
    binary_dir = os.path.dirname(binary_path)
    
    process = subprocess.Popen(
        [binary_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=binary_dir,
        bufsize=1
    )
    
    def send_cmd(cmd, delay=0.1):
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
        time.sleep(delay)
    
    send_cmd("uci", 0.3)
    send_cmd("isready", 0.2)
    send_cmd(f"position fen {fen}", 0.1)
    send_cmd(f"go depth {depth}", 5)
    send_cmd("quit", 0.1)
    
    stdout, stderr = process.communicate(timeout=15)
    
    # Extract final evaluation
    final_eval = None
    best_move = None
    for line in reversed(stdout.split('\n')):
        if 'score cp' in line and final_eval is None:
            match = re.search(r'score cp ([+-]?\d+)', line)
            if match:
                final_eval = int(match.group(1))
        if 'bestmove' in line and best_move is None:
            match = re.search(r'bestmove (\S+)', line)
            if match:
                best_move = match.group(1)
        if final_eval is not None and best_move is not None:
            break
    
    return final_eval, best_move

# Stockfish reference values (from previous analysis)
stockfish_evals = {
    60: 197,
    98: -506,
    103: -36,
}

print("="*80)
print("COMPARISON: Original RubiChess vs Modified (Phase 1) RubiChess")
print("="*80)

results = {}

for name, binary_path in binaries.items():
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"Path: {binary_path}")
    print(f"Exists: {os.path.exists(binary_path)}")
    print(f"{'='*80}")
    
    if not os.path.exists(binary_path):
        print("SKIPPED - file not found")
        continue
    
    results[name] = {}
    
    for pos_id, (pos_type, fen) in positions.items():
        print(f"\n  Position {pos_id} ({pos_type}):")
        print(f"    FEN: {fen[:50]}...")
        
        try:
            eval_cp, best_move = get_evaluation(binary_path, fen)
            results[name][pos_id] = eval_cp
            sf_eval = stockfish_evals[pos_id]
            diff = eval_cp - sf_eval if eval_cp else "N/A"
            
            print(f"    Evaluation: {eval_cp:+d} cp")
            print(f"    Best move:  {best_move}")
            print(f"    Stockfish:  {sf_eval:+d} cp")
            print(f"    Difference: {diff:+d} cp" if isinstance(diff, int) else f"    Difference: {diff}")
        except Exception as e:
            print(f"    ERROR: {e}")
            results[name][pos_id] = None

# Summary comparison
print("\n" + "="*80)
print("SUMMARY COMPARISON")
print("="*80)

print(f"\n{'Position':<12} {'Type':<15} {'Original':>12} {'Modified':>12} {'Stockfish':>12} {'Orig-SF':>10} {'Mod-SF':>10}")
print("-"*85)

for pos_id, (pos_type, fen) in positions.items():
    orig = results.get("Original", {}).get(pos_id, "N/A")
    mod = results.get("Modified (Phase 1)", {}).get(pos_id, "N/A")
    sf = stockfish_evals[pos_id]
    
    orig_str = f"{orig:+d}" if isinstance(orig, int) else str(orig)
    mod_str = f"{mod:+d}" if isinstance(mod, int) else str(mod)
    sf_str = f"{sf:+d}"
    
    orig_diff = f"{orig - sf:+d}" if isinstance(orig, int) else "N/A"
    mod_diff = f"{mod - sf:+d}" if isinstance(mod, int) else "N/A"
    
    print(f"{pos_id:<12} {pos_type:<15} {orig_str:>12} {mod_str:>12} {sf_str:>12} {orig_diff:>10} {mod_diff:>10}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

if "Original" in results and "Modified (Phase 1)" in results:
    same_issue = True
    for pos_id in positions:
        orig = results["Original"].get(pos_id)
        mod = results["Modified (Phase 1)"].get(pos_id)
        if orig is not None and mod is not None:
            if abs(orig - mod) > 50:  # More than 50cp difference
                same_issue = False
                print(f"\nPosition {pos_id}: DIFFERENT evaluations (Original: {orig}, Modified: {mod})")
    
    if same_issue:
        print("\nBoth versions show SIMILAR evaluation discrepancies vs Stockfish.")
        print("This indicates the issue is NOT caused by Phase 1 changes.")
        print("The discrepancy exists in the original NNUE network.")
    else:
        print("\nThe versions show DIFFERENT evaluations.")
        print("Phase 1 changes may have affected the evaluation.")
