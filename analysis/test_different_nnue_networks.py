#!/usr/bin/env python3
"""
Test different NNUE networks from the official RubiChess repository
https://github.com/Matthies/NN
"""
import subprocess
import os
import time
import re
import urllib.request

# RubiChess binary
rubichess_path = r"D:\Windsurf\RubiChessAdvanced\RubiChess\x64\Release\RubiChess.exe"
rubichess_dir = os.path.dirname(rubichess_path)

# Available NNUE networks from https://github.com/Matthies/NN
# Sorted by date (newest first)
nnue_networks = {
    "nn-f05142b28f-20250520": "https://github.com/Matthies/NN/raw/main/nn-f05142b28f-20250520.nnue",  # Current (May 2025)
    "nn-c257b2ebf1-20230812": "https://github.com/Matthies/NN/raw/main/nn-c257b2ebf1-20230812.nnue",  # Aug 2023
    "nn-eb5456adef-20230801": "https://github.com/Matthies/NN/raw/main/nn-eb5456adef-20230801.nnue",  # Aug 2023
    "nn-d901a1822f-20230606": "https://github.com/Matthies/NN/raw/main/nn-d901a1822f-20230606.nnue",  # Jun 2023
    "nn-fdccaaabd3-20230314": "https://github.com/Matthies/NN/raw/main/nn-fdccaaabd3-20230314.nnue",  # Mar 2023
    "nn-df29ab9d61-20220831": "https://github.com/Matthies/NN/raw/main/nn-df29ab9d61-20220831.nnue",  # Aug 2022
}

# Test positions - expanded set covering different position types
# Format: pos_id: (type, fen, stockfish_eval)
positions = {
    # Original problematic positions
    60: ("Opening", "r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/3PbN2/PPP2PPP/RNBQ1RK1 w kq - 1 6", 197),
    98: ("Pawn EG", "8/8/2k5/5p2/6p1/2K5/3P4/8 b - - 1 1", -506),
    103: ("Pawn EG", "8/8/1p1k4/3p4/3P4/1P6/4K3/8 b - - 1 1", -36),
    
    # Additional opening positions
    1: ("Opening", "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", 30),  # 1.e4
    2: ("Opening", "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1", 30),  # 1.d4
    3: ("Sicilian", "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2", 50),
    
    # Middlegame positions
    10: ("Middlegame", "r1bq1rk1/ppp2ppp/2n2n2/3pp3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 w - - 0 7", 20),
    11: ("Middlegame", "r2qkb1r/ppp2ppp/2n1bn2/3pp3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 4 5", 0),
    
    # Rook endgames (relevant to Phase 1)
    20: ("Rook EG", "8/8/4k3/8/8/4K3/4P3/4R3 w - - 0 1", 500),  # K+R+P vs K
    21: ("Rook EG", "8/4k3/8/8/8/4K3/8/4R3 w - - 0 1", 500),  # K+R vs K
    
    # Complex endgames
    30: ("Complex EG", "8/5k2/8/5P2/5K2/8/8/8 w - - 0 1", 800),  # K+P vs K (winning)
    31: ("Complex EG", "8/8/8/4k3/8/4PK2/8/8 w - - 0 1", 600),  # K+P vs K
    
    # Tactical positions
    40: ("Tactical", "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4", 0),  # Scholar's mate threat
    41: ("Tactical", "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3", 50),  # Italian Game
    
    # Quiet strategic positions
    50: ("Strategic", "r1bq1rk1/pp2ppbp/2np1np1/8/3NP3/2N1BP2/PPPQ2PP/R3KB1R w KQ - 0 9", 30),
    51: ("Strategic", "r2q1rk1/ppp2ppp/2n1bn2/3p4/3P4/2NBPN2/PP3PPP/R2QK2R w KQ - 0 9", 10),
}

def download_network(name, url, dest_dir):
    """Download NNUE network if not already present"""
    dest_path = os.path.join(dest_dir, name + ".nnue")
    if os.path.exists(dest_path):
        print(f"  [EXISTS] {name}.nnue")
        return dest_path
    
    print(f"  [DOWNLOADING] {name}.nnue...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"  [OK] Downloaded to {dest_path}")
        return dest_path
    except Exception as e:
        print(f"  [ERROR] Failed to download: {e}")
        return None

def get_evaluation(binary_path, fen, nnue_path=None, depth=10):
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
    if nnue_path:
        send_cmd(f"setoption name NNUENetpath value {nnue_path}", 0.3)
    send_cmd("isready", 0.3)
    send_cmd(f"position fen {fen}", 0.1)
    send_cmd(f"go depth {depth}", 3)  # Reduced timeout for faster testing
    send_cmd("quit", 0.1)
    
    stdout, stderr = process.communicate(timeout=10)
    
    # Extract final evaluation
    final_eval = None
    for line in reversed(stdout.split('\n')):
        if 'score cp' in line:
            match = re.search(r'score cp ([+-]?\d+)', line)
            if match:
                final_eval = int(match.group(1))
                break
    
    return final_eval

print("="*80)
print("TESTING DIFFERENT NNUE NETWORKS - EXPANDED TEST")
print("="*80)
print(f"\nRubiChess: {rubichess_path}")
print(f"Networks will be downloaded to: {rubichess_dir}")
print(f"Testing {len(positions)} positions across {len(set(p[0] for p in positions.values()))} position types")

# Test which networks to download
networks_to_test = [
    "nn-f05142b28f-20250520",  # Current (May 2025)
    "nn-c257b2ebf1-20230812",  # Aug 2023
    "nn-d901a1822f-20230606",  # Jun 2023
]

print(f"\nDownloading networks...")
for name in networks_to_test:
    url = nnue_networks[name]
    download_network(name, url, rubichess_dir)

# Test each network
results = {}

for net_name in networks_to_test:
    net_path = os.path.join(rubichess_dir, net_name + ".nnue")
    if not os.path.exists(net_path):
        print(f"\n[SKIP] {net_name} - not available")
        continue
    
    print(f"\n{'='*80}")
    print(f"Testing: {net_name}")
    print(f"{'='*80}")
    
    results[net_name] = {}
    
    for pos_id in sorted(positions.keys()):
        pos_type, fen, sf_eval = positions[pos_id]
        try:
            eval_cp = get_evaluation(rubichess_path, fen, net_path)
            results[net_name][pos_id] = eval_cp
            diff = eval_cp - sf_eval if eval_cp is not None else None
            
            if diff is not None:
                print(f"  Pos {pos_id:3d} ({pos_type:10}): {eval_cp:+6d} cp  (SF: {sf_eval:+5d}, diff: {diff:+5d})")
            else:
                print(f"  Pos {pos_id:3d} ({pos_type:10}): ERROR")
        except Exception as e:
            print(f"  Pos {pos_id:3d} ({pos_type:10}): ERROR - {e}")
            results[net_name][pos_id] = None

# Detailed Summary by Position Type
print("\n" + "="*80)
print("SUMMARY BY POSITION TYPE")
print("="*80)

# Group positions by type
pos_types = {}
for pos_id, (pos_type, fen, sf_eval) in positions.items():
    if pos_type not in pos_types:
        pos_types[pos_type] = []
    pos_types[pos_type].append(pos_id)

for pos_type, pos_ids in sorted(pos_types.items()):
    print(f"\n{pos_type}:")
    print(f"  {'Network':<30} {'Avg Diff':>10} {'Max Diff':>10}")
    print(f"  {'-'*52}")
    
    for net_name in networks_to_test:
        if net_name not in results:
            continue
        
        diffs = []
        for pos_id in pos_ids:
            eval_cp = results[net_name].get(pos_id)
            if eval_cp is not None:
                sf_eval = positions[pos_id][2]
                diffs.append(abs(eval_cp - sf_eval))
        
        if diffs:
            avg_diff = sum(diffs) / len(diffs)
            max_diff = max(diffs)
            print(f"  {net_name:<30} {avg_diff:>10.0f} {max_diff:>10d}")

# Overall Summary
print("\n" + "="*80)
print("OVERALL SUMMARY")
print("="*80)

print(f"\n{'Network':<30} {'Avg Diff':>10} {'Total Diff':>12} {'Positions':>10}")
print("-"*65)

best_network = None
best_avg = float('inf')

for net_name in networks_to_test:
    if net_name not in results:
        continue
    
    diffs = []
    for pos_id in positions:
        eval_cp = results[net_name].get(pos_id)
        if eval_cp is not None:
            sf_eval = positions[pos_id][2]
            diffs.append(abs(eval_cp - sf_eval))
    
    if diffs:
        avg_diff = sum(diffs) / len(diffs)
        total_diff = sum(diffs)
        print(f"{net_name:<30} {avg_diff:>10.1f} {total_diff:>12d} {len(diffs):>10d}")
        
        if avg_diff < best_avg:
            best_avg = avg_diff
            best_network = net_name

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)
if best_network:
    print(f"\nBest network for evaluation accuracy: {best_network}")
    print(f"Average difference from Stockfish: {best_avg:.1f} cp")
else:
    print("\nNo conclusive recommendation - need more data.")
