#!/usr/bin/env python3
"""
Tactical Depth Analysis - Compare RubiChess vs Stockfish at different depths
to understand where tactical differences emerge
"""
import subprocess
import os
import time
import re

rubichess_path = r"D:\Windsurf\RubiChessAdvanced\RubiChess\x64\Release\RubiChess.exe"
stockfish_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
rubichess_dir = os.path.dirname(rubichess_path)

# Tactical positions where we want to compare depth-by-depth
POSITIONS = {
    "pos_60": ("r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/3PbN2/PPP2PPP/RNBQ1RK1 w kq - 1 6", 
               "Opening - White to move"),
    "pos_98": ("8/8/2k5/5p2/6p1/2K5/3P4/8 b - - 1 1",
               "Pawn endgame - Black to move"),
    "pos_103": ("8/8/1p1k4/3p4/3P4/1P6/4K3/8 b - - 1 1",
                "Pawn endgame - Black to move"),
    "tactical_1": ("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4",
                   "Scholar's mate threat"),
    "tactical_2": ("r1b1k2r/ppppqppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 w kq - 0 6",
                   "Complex tactical position"),
}

def run_engine_search(engine_path, fen, depth, use_june2023_net=False):
    """Run engine search and return results"""
    engine_dir = os.path.dirname(engine_path)
    
    process = subprocess.Popen(
        [engine_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=engine_dir if "RubiChess" in engine_path else None,
        bufsize=1
    )
    
    def send_cmd(cmd, delay=0.1):
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
        time.sleep(delay)
    
    send_cmd("uci", 0.3)
    if use_june2023_net and "RubiChess" in engine_path:
        send_cmd("setoption name NNUENetpath value nn-d901a1822f-20230606.nnue", 0.2)
    send_cmd("isready", 0.2)
    send_cmd(f"position fen {fen}", 0.1)
    send_cmd(f"go depth {depth}", 10)
    send_cmd("quit", 0.1)
    
    stdout, stderr = process.communicate(timeout=30)
    
    # Extract depth-by-depth results
    results = []
    for line in stdout.split('\n'):
        if 'info depth' in line and 'score cp' in line and 'upperbound' not in line and 'lowerbound' not in line:
            depth_match = re.search(r'depth (\d+)', line)
            score_match = re.search(r'score cp ([+-]?\d+)', line)
            nodes_match = re.search(r'nodes (\d+)', line)
            pv_match = re.search(r'pv (.+?)(?:\s*$)', line)
            
            if depth_match and score_match:
                results.append({
                    'depth': int(depth_match.group(1)),
                    'score': int(score_match.group(1)),
                    'nodes': int(nodes_match.group(1)) if nodes_match else 0,
                    'pv': pv_match.group(1).split()[0] if pv_match else ""
                })
    
    return results

print("="*80)
print("TACTICAL DEPTH ANALYSIS: RubiChess vs Stockfish")
print("="*80)

for pos_name, (fen, desc) in POSITIONS.items():
    print(f"\n{'='*80}")
    print(f"Position: {pos_name}")
    print(f"Description: {desc}")
    print(f"FEN: {fen}")
    print(f"{'='*80}")
    
    # Run both engines
    print("\nRunning RubiChess (June 2023 network)...")
    rubi_results = run_engine_search(rubichess_path, fen, 15, use_june2023_net=True)
    
    print("Running Stockfish...")
    sf_results = run_engine_search(stockfish_path, fen, 15)
    
    # Compare depth by depth
    print(f"\n{'Depth':>6} {'RubiChess':>12} {'Stockfish':>12} {'Diff':>10} {'RC Move':>10} {'SF Move':>10}")
    print("-"*65)
    
    max_depth = max(
        max(r['depth'] for r in rubi_results) if rubi_results else 0,
        max(r['depth'] for r in sf_results) if sf_results else 0
    )
    
    for d in range(1, min(max_depth + 1, 16)):
        rubi = next((r for r in rubi_results if r['depth'] == d), None)
        sf = next((r for r in sf_results if r['depth'] == d), None)
        
        rubi_score = rubi['score'] if rubi else None
        sf_score = sf['score'] if sf else None
        rubi_move = rubi['pv'] if rubi else ""
        sf_move = sf['pv'] if sf else ""
        
        diff = (rubi_score - sf_score) if rubi_score is not None and sf_score is not None else None
        
        rubi_str = f"{rubi_score:+d}" if rubi_score is not None else "N/A"
        sf_str = f"{sf_score:+d}" if sf_score is not None else "N/A"
        diff_str = f"{diff:+d}" if diff is not None else "N/A"
        
        # Highlight significant differences
        marker = ""
        if diff is not None and abs(diff) > 100:
            marker = " ***"
        elif diff is not None and abs(diff) > 50:
            marker = " **"
        elif diff is not None and abs(diff) > 25:
            marker = " *"
        
        move_match = "same" if rubi_move == sf_move else "DIFF"
        
        print(f"{d:>6} {rubi_str:>12} {sf_str:>12} {diff_str:>10}{marker} {rubi_move:>10} {sf_move:>10} {move_match if rubi_move and sf_move else ''}")

print("\n" + "="*80)
print("ANALYSIS SUMMARY")
print("="*80)
print("""
Legend:
  *** = Difference > 100cp (significant)
  **  = Difference > 50cp (notable)
  *   = Difference > 25cp (minor)
  
Key observations:
- Large differences at low depths may indicate evaluation differences
- Differences that persist at high depths suggest fundamental disagreement
- Move differences are more important than score differences
""")
