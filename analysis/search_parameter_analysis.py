#!/usr/bin/env python3
"""
Search Parameter Analysis for RubiChess
Tests different search parameter configurations to improve tactical play
"""
import subprocess
import os
import time
import re

rubichess_path = r"D:\Windsurf\RubiChessAdvanced\RubiChess\x64\Release\RubiChess.exe"
rubichess_dir = os.path.dirname(rubichess_path)

# Key search parameters that affect tactical play
# Format: (name, default_value, description, tactical_impact)
SEARCH_PARAMS = {
    # Extensions - more extensions = deeper tactical search
    "extguardcheckext": (3, "Check extension guard limit", "HIGH"),
    "extguarddoubleext": (8, "Double extension guard limit", "HIGH"),
    "singularmindepth": (8, "Min depth for singular extension", "HIGH"),
    "singularmarginfor2": (23, "Margin for double singular extension", "MEDIUM"),
    
    # History extension thresholds
    "histextminthreshold": (9, "History extension min threshold", "MEDIUM"),
    "histextmaxthreshold": (16, "History extension max threshold", "MEDIUM"),
    
    # Pruning - less aggressive = more tactical accuracy
    "razormargin": (347, "Razoring margin", "HIGH"),
    "razordepthfactor": (53, "Razoring depth factor", "MEDIUM"),
    "futilitymargin": (9, "Futility pruning margin", "HIGH"),
    "futilitymarginperdepth": (69, "Futility margin per depth", "HIGH"),
    "futilityreversedepthfactor": (53, "Reverse futility depth factor", "HIGH"),
    
    # Threat pruning
    "threatprunemargin": (43, "Threat pruning margin", "HIGH"),
    "threatprunemarginimprove": (3, "Threat pruning margin (improved)", "MEDIUM"),
    
    # Null move
    "nmmindepth": (4, "Null move min depth", "MEDIUM"),
    "nmmredbase": (1, "Null move reduction base", "MEDIUM"),
    
    # LMR (Late Move Reductions)
    "lmrmindepth": (2, "LMR min depth", "MEDIUM"),
    "lmrstatsratio": (884, "LMR stats ratio", "LOW"),
    
    # SEE pruning
    "seeprunemarginperdepth": (-13, "SEE prune margin per depth", "HIGH"),
    
    # ProbCut
    "probcutmindepth": (7, "ProbCut min depth", "MEDIUM"),
    "probcutmargin": (110, "ProbCut margin", "MEDIUM"),
}

# Tactical test positions - positions where tactics matter
TACTICAL_POSITIONS = {
    # Positions with tactical complications
    "mate_threat": ("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4", 
                    "Scholar's mate threat - White should see Qxf7#"),
    "pin_tactic": ("r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
                   "Italian Game - tactical potential"),
    "fork_threat": ("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
                    "Knight fork potential"),
    "discovered_attack": ("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5",
                          "Discovered attack potential"),
    "sacrifice": ("r1bqkb1r/pppp1ppp/2n2n2/4p3/2BPP3/5N2/PPP2PPP/RNBQK2R b KQkq d3 0 4",
                  "Pawn sacrifice position"),
    
    # Original problematic positions
    "pos_60": ("r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/3PbN2/PPP2PPP/RNBQ1RK1 w kq - 1 6", 
               "Opening with tactical elements"),
    "pos_98": ("8/8/2k5/5p2/6p1/2K5/3P4/8 b - - 1 1",
               "Pawn endgame"),
    "pos_103": ("8/8/1p1k4/3p4/3P4/1P6/4K3/8 b - - 1 1",
                "Pawn endgame"),
}

def run_search(fen, depth=12, params=None):
    """Run RubiChess search with optional parameter overrides"""
    process = subprocess.Popen(
        [rubichess_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=rubichess_dir,
        bufsize=1
    )
    
    def send_cmd(cmd, delay=0.1):
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
        time.sleep(delay)
    
    send_cmd("uci", 0.3)
    # Use June 2023 network
    send_cmd("setoption name NNUENetpath value nn-d901a1822f-20230606.nnue", 0.2)
    
    # Apply parameter overrides if provided
    if params:
        for name, value in params.items():
            send_cmd(f"setoption name {name} value {value}", 0.1)
    
    send_cmd("isready", 0.2)
    send_cmd(f"position fen {fen}", 0.1)
    send_cmd(f"go depth {depth}", 5)
    send_cmd("quit", 0.1)
    
    stdout, stderr = process.communicate(timeout=15)
    
    # Extract results
    result = {
        "eval": None,
        "nodes": None,
        "depth": None,
        "best_move": None,
        "nps": None,
    }
    
    for line in reversed(stdout.split('\n')):
        if 'score cp' in line and result["eval"] is None:
            match = re.search(r'score cp ([+-]?\d+)', line)
            if match:
                result["eval"] = int(match.group(1))
            match = re.search(r'nodes (\d+)', line)
            if match:
                result["nodes"] = int(match.group(1))
            match = re.search(r'depth (\d+)', line)
            if match:
                result["depth"] = int(match.group(1))
            match = re.search(r'nps (\d+)', line)
            if match:
                result["nps"] = int(match.group(1))
        if 'bestmove' in line and result["best_move"] is None:
            match = re.search(r'bestmove (\S+)', line)
            if match:
                result["best_move"] = match.group(1)
    
    return result

print("="*80)
print("SEARCH PARAMETER ANALYSIS FOR TACTICAL PLAY")
print("="*80)

# First, get baseline results with default parameters
print("\n" + "="*80)
print("BASELINE RESULTS (Default Parameters)")
print("="*80)

baseline_results = {}
for name, (fen, desc) in TACTICAL_POSITIONS.items():
    result = run_search(fen)
    baseline_results[name] = result
    print(f"\n{name}: {desc[:50]}...")
    print(f"  Eval: {result['eval']:+d} cp" if result['eval'] else "  Eval: N/A")
    print(f"  Best: {result['best_move']}")
    print(f"  Nodes: {result['nodes']:,}" if result['nodes'] else "  Nodes: N/A")

# Test with more aggressive extension settings
print("\n" + "="*80)
print("TEST 1: More Aggressive Extensions")
print("="*80)
print("Increasing extension limits to search deeper in tactical positions")

aggressive_ext_params = {
    "extguardcheckext": 5,      # Default: 3, increase to allow more check extensions
    "extguarddoubleext": 12,    # Default: 8, increase to allow more double extensions
    "singularmindepth": 6,      # Default: 8, lower to trigger singular extension earlier
}

print(f"\nParameters: {aggressive_ext_params}")

ext_results = {}
for name, (fen, desc) in TACTICAL_POSITIONS.items():
    result = run_search(fen, params=aggressive_ext_params)
    ext_results[name] = result
    
    baseline = baseline_results[name]
    eval_diff = (result['eval'] - baseline['eval']) if result['eval'] and baseline['eval'] else 0
    node_diff = ((result['nodes'] - baseline['nodes']) / baseline['nodes'] * 100) if result['nodes'] and baseline['nodes'] else 0
    
    print(f"\n{name}:")
    print(f"  Eval: {result['eval']:+d} cp (diff: {eval_diff:+d})" if result['eval'] else "  Eval: N/A")
    print(f"  Nodes: {result['nodes']:,} ({node_diff:+.1f}%)" if result['nodes'] else "  Nodes: N/A")
    print(f"  Move: {result['best_move']} {'(same)' if result['best_move'] == baseline['best_move'] else '(CHANGED from ' + str(baseline['best_move']) + ')'}")

# Test with less aggressive pruning
print("\n" + "="*80)
print("TEST 2: Less Aggressive Pruning")
print("="*80)
print("Reducing pruning to avoid missing tactical shots")

less_pruning_params = {
    "razormargin": 400,         # Default: 347, increase to prune less
    "futilitymargin": 12,       # Default: 9, increase to prune less
    "threatprunemargin": 60,    # Default: 43, increase to prune less
    "seeprunemarginperdepth": -8,  # Default: -13, less negative = prune less
}

print(f"\nParameters: {less_pruning_params}")

prune_results = {}
for name, (fen, desc) in TACTICAL_POSITIONS.items():
    result = run_search(fen, params=less_pruning_params)
    prune_results[name] = result
    
    baseline = baseline_results[name]
    eval_diff = (result['eval'] - baseline['eval']) if result['eval'] and baseline['eval'] else 0
    node_diff = ((result['nodes'] - baseline['nodes']) / baseline['nodes'] * 100) if result['nodes'] and baseline['nodes'] else 0
    
    print(f"\n{name}:")
    print(f"  Eval: {result['eval']:+d} cp (diff: {eval_diff:+d})" if result['eval'] else "  Eval: N/A")
    print(f"  Nodes: {result['nodes']:,} ({node_diff:+.1f}%)" if result['nodes'] else "  Nodes: N/A")
    print(f"  Move: {result['best_move']} {'(same)' if result['best_move'] == baseline['best_move'] else '(CHANGED from ' + str(baseline['best_move']) + ')'}")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print("\nEvaluation Changes (vs Baseline):")
print(f"{'Position':<20} {'Baseline':>10} {'Ext+':>10} {'Prune-':>10}")
print("-"*55)

for name in TACTICAL_POSITIONS:
    base = baseline_results[name]['eval'] or 0
    ext = ext_results[name]['eval'] or 0
    prune = prune_results[name]['eval'] or 0
    print(f"{name:<20} {base:>+10d} {ext:>+10d} {prune:>+10d}")

print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)
print("""
Based on the analysis:

1. If 'More Extensions' shows better tactical accuracy without
   significant node increase, consider adopting those parameters.

2. If 'Less Pruning' finds better moves but with much higher node
   counts, it may be too slow for practical play.

3. The ideal configuration balances tactical accuracy with search speed.
""")
