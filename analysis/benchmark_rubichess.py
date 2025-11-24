#!/usr/bin/env python3
"""
Benchmark RubiChess to measure NPS (nodes per second)
"""
import subprocess
import os
import time
import re

rubichess_avx2_path = r"D:\Windsurf\RubiChessAdvanced\RubiChess\x64\Release\RubiChess.exe"
rubichess_avx512_path = r"D:\Windsurf\RubiChessAdvanced\RubiChess\src\Release-optimal\RubiChess_avx512.exe"
rubichess_dir_avx2 = os.path.dirname(rubichess_avx2_path)
rubichess_dir_avx512 = os.path.dirname(rubichess_avx512_path)

# Benchmark positions
POSITIONS = [
    ("startpos", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
    ("kiwipete", "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"),
    ("pos3", "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"),
]

def run_benchmark(engine_path, engine_dir, fen, movetime=5000):
    """Run search and extract NPS"""
    process = subprocess.Popen(
        [engine_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=engine_dir,
        bufsize=1
    )
    
    def send_cmd(cmd, delay=0.1):
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
        time.sleep(delay)
    
    send_cmd("uci", 0.3)
    send_cmd("setoption name NNUENetpath value nn-d901a1822f-20230606.nnue", 0.2)
    send_cmd("isready", 0.5)  # Wait for network to load
    send_cmd(f"position fen {fen}", 0.1)
    
    start_time = time.time()
    # Use movetime for consistent benchmark
    send_cmd(f"go movetime {movetime}", 0.1)
    
    # Wait for bestmove
    stdout_lines = []
    while True:
        line = process.stdout.readline()
        stdout_lines.append(line)
        if 'bestmove' in line:
            break
        if time.time() - start_time > 30:
            break
    
    send_cmd("quit", 0.1)
    process.wait(timeout=5)
    
    stdout = ''.join(stdout_lines)
    elapsed = time.time() - start_time
    
    # Extract final NPS and nodes
    nps = None
    nodes = None
    final_depth = None
    
    for line in stdout.split('\n'):
        if 'info depth' in line and 'nps' in line:
            nps_match = re.search(r'nps (\d+)', line)
            nodes_match = re.search(r'nodes (\d+)', line)
            depth_match = re.search(r'depth (\d+)', line)
            
            if nps_match:
                nps = int(nps_match.group(1))
            if nodes_match:
                nodes = int(nodes_match.group(1))
            if depth_match:
                final_depth = int(depth_match.group(1))
    
    return {
        'nps': nps,
        'nodes': nodes,
        'depth': final_depth,
        'time': elapsed
    }

def benchmark_engine(name, engine_path, engine_dir):
    """Benchmark a single engine"""
    print(f"\n{'='*70}")
    print(f"BENCHMARKING: {name}")
    print(f"{'='*70}")
    print(f"Binary: {engine_path}")
    
    # Check what features the engine reports
    process = subprocess.Popen(
        [engine_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=engine_dir,
        bufsize=1
    )
    
    process.stdin.write("uci\n")
    process.stdin.flush()
    time.sleep(0.5)
    process.stdin.write("quit\n")
    process.stdin.flush()
    stdout, _ = process.communicate(timeout=5)
    
    for line in stdout.split('\n'):
        if 'id name' in line:
            print(f"Engine: {line.strip().replace('id name ', '')}")
    
    total_nps = 0
    count = 0
    results = []
    
    for pos_name, fen in POSITIONS:
        result = run_benchmark(engine_path, engine_dir, fen, movetime=5000)
        
        if result['nps']:
            total_nps += result['nps']
            count += 1
            results.append((pos_name, result['nps'], result['nodes']))
            print(f"  {pos_name}: {result['nps']:,} NPS")
        else:
            print(f"  {pos_name}: ERROR")
    
    avg_nps = total_nps / count if count > 0 else 0
    return avg_nps, results

print("="*70)
print("RUBICHESS PERFORMANCE COMPARISON: AVX2 vs AVX-512")
print("="*70)

# Benchmark AVX2 build
avx2_nps, avx2_results = benchmark_engine("AVX2 Build (Original)", rubichess_avx2_path, rubichess_dir_avx2)

# Benchmark AVX-512 build
avx512_nps, avx512_results = benchmark_engine("AVX-512 Build (Optimized)", rubichess_avx512_path, rubichess_dir_avx512)

# Summary
print("\n" + "="*70)
print("COMPARISON SUMMARY")
print("="*70)

print(f"\n{'Position':<15} {'AVX2 NPS':>15} {'AVX-512 NPS':>15} {'Improvement':>12}")
print("-"*60)

for i, (pos_name, _) in enumerate(POSITIONS):
    avx2 = avx2_results[i][1] if i < len(avx2_results) else 0
    avx512 = avx512_results[i][1] if i < len(avx512_results) else 0
    improvement = ((avx512 - avx2) / avx2 * 100) if avx2 > 0 else 0
    print(f"{pos_name:<15} {avx2:>15,} {avx512:>15,} {improvement:>+11.1f}%")

print("-"*60)
overall_improvement = ((avx512_nps - avx2_nps) / avx2_nps * 100) if avx2_nps > 0 else 0
print(f"{'AVERAGE':<15} {avx2_nps:>15,.0f} {avx512_nps:>15,.0f} {overall_improvement:>+11.1f}%")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
if overall_improvement > 0:
    print(f"\n[OK] AVX-512 build is {overall_improvement:.1f}% FASTER than AVX2 build!")
else:
    print(f"\n[!] AVX-512 build is {abs(overall_improvement):.1f}% slower (unexpected)")
print(f"\nRecommendation: Use the AVX-512 optimized build for best performance.")
