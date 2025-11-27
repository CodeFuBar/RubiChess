#!/usr/bin/env python3
"""
PGO Profiling Script for RubiChess
Runs the instrumented engine through various workloads to generate profile data.
"""
import subprocess
import time
import sys
import os

# Profiling positions - diverse set for good coverage
POSITIONS = [
    # Opening positions
    ("startpos", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 14),
    ("sicilian", "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2", 14),
    ("queens_gambit", "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2", 14),
    
    # Middlegame tactical positions
    ("kiwipete", "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", 14),
    ("tactical1", "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4", 14),
    ("tactical2", "r2qkbnr/ppp2ppp/2n5/3pp3/2B1P1b1/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 5", 14),
    
    # Complex middlegame
    ("complex1", "r1bq1rk1/pp2ppbp/2np1np1/8/2BNP3/2N1B3/PPP2PPP/R2QK2R w KQ - 0 9", 14),
    ("complex2", "r2q1rk1/1p2bppp/p1n1bn2/3p4/3NP3/1BN1BP2/PPP3PP/R2Q1RK1 w - - 0 12", 14),
    
    # Endgame positions
    ("endgame1", "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", 16),
    ("endgame2", "8/8/4k3/8/2p5/8/B2K4/8 w - - 0 1", 18),
    ("endgame3", "8/k7/3p4/p2P1p2/P2P1P2/8/8/K7 w - - 0 1", 18),
    
    # Pawn structure positions
    ("pawns1", "rnbqkb1r/pp1p1pPp/8/2p1pP2/1P1P4/3P3P/P1P1P3/RNBQKBNR w KQkq e6 0 1", 14),
    
    # Rook endgames
    ("rook_end1", "8/8/1k6/8/8/1K6/1R6/r7 w - - 0 1", 18),
    ("rook_end2", "6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1", 16),
]

def run_profiling(engine_path):
    """Run the engine through profiling workload"""
    print("="*70)
    print("RubiChess PGO Profiling Script")
    print("="*70)
    print(f"\nEngine: {engine_path}")
    print(f"Positions: {len(POSITIONS)}")
    print()
    
    if not os.path.exists(engine_path):
        print(f"ERROR: Engine not found: {engine_path}")
        return False
    
    engine_dir = os.path.dirname(engine_path)
    
    # Start the engine
    print("Starting engine...")
    process = subprocess.Popen(
        [engine_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=engine_dir,
        bufsize=1
    )
    
    def send_command(cmd, wait_for=None, timeout=120):
        """Send command and optionally wait for response"""
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
        
        if wait_for:
            start = time.time()
            while time.time() - start < timeout:
                line = process.stdout.readline()
                if wait_for in line:
                    return line
                if not line:
                    break
            return None
        return True
    
    try:
        # Initialize UCI
        print("Initializing UCI protocol...")
        send_command("uci")
        time.sleep(0.5)
        
        # Set options
        send_command("setoption name Hash value 256")
        send_command("setoption name Threads value 1")
        
        # Wait for ready
        send_command("isready")
        time.sleep(0.5)
        
        # Run through all positions
        total_nodes = 0
        for i, (name, fen, depth) in enumerate(POSITIONS):
            print(f"\n[{i+1}/{len(POSITIONS)}] {name} (depth {depth})...")
            
            # Set position
            if fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
                send_command("position startpos")
            else:
                send_command(f"position fen {fen}")
            
            # Search
            send_command(f"go depth {depth}")
            
            # Wait for bestmove
            start_time = time.time()
            while time.time() - start_time < 120:
                line = process.stdout.readline()
                if "bestmove" in line:
                    break
                if "nodes" in line:
                    # Extract nodes for progress
                    try:
                        nodes = int(line.split("nodes")[1].split()[0])
                        total_nodes = max(total_nodes, nodes)
                    except:
                        pass
            
            print(f"    Completed.")
        
        # Quit cleanly
        print("\nShutting down engine...")
        send_command("quit")
        time.sleep(1)
        
        # Wait for process to exit
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("\n" + "="*70)
        print("PROFILING COMPLETE")
        print("="*70)
        print(f"\nTotal positions processed: {len(POSITIONS)}")
        print("Profile data should now be in .pgc files")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        try:
            process.kill()
        except:
            pass
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to instrumented executable
        engine = "RubiChess_pgo_instr.exe"
    else:
        engine = sys.argv[1]
    
    # Make path absolute if needed
    if not os.path.isabs(engine):
        engine = os.path.join(os.path.dirname(__file__), engine)
    
    success = run_profiling(engine)
    sys.exit(0 if success else 1)
