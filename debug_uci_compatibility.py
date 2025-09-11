#!/usr/bin/env python3
"""
Debug UCI compatibility issues with the modified RubiChess engine.
Tests basic UCI protocol communication to identify ChessBase compatibility problems.
"""

import subprocess
import time
import sys
from pathlib import Path

def test_uci_protocol(engine_path: str, engine_name: str) -> dict:
    """Test basic UCI protocol communication with engine."""
    print(f"\n=== Testing {engine_name} ===")
    print(f"Path: {engine_path}")
    
    if not Path(engine_path).exists():
        return {"success": False, "error": "Engine file not found"}
    
    try:
        # Start engine process
        process = subprocess.Popen(
            engine_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        def send_command(cmd: str) -> list:
            """Send UCI command and read response."""
            print(f">>> {cmd}")
            process.stdin.write(cmd + '\n')
            process.stdin.flush()
            
            responses = []
            start_time = time.time()
            
            while time.time() - start_time < 5.0:  # 5 second timeout
                if process.poll() is not None:
                    break
                    
                try:
                    line = process.stdout.readline()
                    if line:
                        line = line.strip()
                        print(f"<<< {line}")
                        responses.append(line)
                        
                        # Check for command completion
                        if cmd == "uci" and line == "uciok":
                            break
                        elif cmd == "isready" and line == "readyok":
                            break
                        elif cmd.startswith("go") and line.startswith("bestmove"):
                            break
                except:
                    break
            
            return responses
        
        # Test UCI protocol sequence
        results = {}
        
        # 1. UCI identification
        print("\n1. Testing UCI identification...")
        uci_response = send_command("uci")
        results["uci_ok"] = any("uciok" in resp for resp in uci_response)
        results["engine_id"] = [resp for resp in uci_response if resp.startswith("id name")]
        
        if not results["uci_ok"]:
            process.terminate()
            return {"success": False, "error": "No uciok response", "details": results}
        
        # 2. Ready check
        print("\n2. Testing ready state...")
        ready_response = send_command("isready")
        results["ready_ok"] = any("readyok" in resp for resp in ready_response)
        
        if not results["ready_ok"]:
            process.terminate()
            return {"success": False, "error": "No readyok response", "details": results}
        
        # 3. New game setup
        print("\n3. Testing new game setup...")
        send_command("ucinewgame")
        send_command("isready")
        
        # 4. Position setup and search
        print("\n4. Testing position and search...")
        send_command("position startpos")
        search_response = send_command("go depth 5")
        results["bestmove"] = [resp for resp in search_response if resp.startswith("bestmove")]
        results["search_ok"] = len(results["bestmove"]) > 0
        
        # 5. Quit
        print("\n5. Sending quit...")
        send_command("quit")
        
        # Wait for process to terminate
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait()
        
        results["success"] = results["uci_ok"] and results["ready_ok"] and results["search_ok"]
        return results
        
    except Exception as e:
        try:
            process.terminate()
        except:
            pass
        return {"success": False, "error": str(e)}

def check_dependencies(engine_path: str) -> dict:
    """Check engine dependencies and runtime requirements."""
    print(f"\n=== Checking Dependencies for {Path(engine_path).name} ===")
    
    results = {}
    
    # Check file properties
    try:
        stat = Path(engine_path).stat()
        results["file_size"] = stat.st_size
        results["executable"] = stat.st_mode & 0o111 != 0
        print(f"File size: {stat.st_size:,} bytes")
        print(f"Executable: {results['executable']}")
    except Exception as e:
        results["file_error"] = str(e)
        print(f"File check error: {e}")
    
    # Check for required files in same directory
    engine_dir = Path(engine_path).parent
    required_files = ["nn-f05142b28f-20250520.nnue"]
    
    results["missing_files"] = []
    for req_file in required_files:
        file_path = engine_dir / req_file
        if file_path.exists():
            print(f"Found: {req_file} ({file_path.stat().st_size:,} bytes)")
        else:
            print(f"MISSING: {req_file}")
            results["missing_files"].append(req_file)
    
    # Try to run with version flag
    try:
        result = subprocess.run([engine_path, "-v"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            results["version_output"] = result.stdout
            print("Version check: OK")
        else:
            results["version_error"] = result.stderr
            print(f"Version check failed: {result.stderr}")
    except Exception as e:
        results["version_exception"] = str(e)
        print(f"Version check exception: {e}")
    
    return results

def main():
    """Main debugging function."""
    print("=== UCI COMPATIBILITY DEBUGGING ===")
    
    engines = {
        "Original RubiChess": r"d:\Windsurf\RubiChessAdvanced\RubiChess\x64\Release\RubiChess.exe",
        "Modified RubiChess": r"d:\Windsurf\RubiChessAdvanced\RubiChess\src\Release-modified\RubiChess_1.1_dev_20250911_001_x86-64-avx2.exe"
    }
    
    for name, path in engines.items():
        if Path(path).exists():
            # Check dependencies
            dep_results = check_dependencies(path)
            
            # Test UCI protocol
            uci_results = test_uci_protocol(path, name)
            
            print(f"\n=== {name} SUMMARY ===")
            print(f"Dependencies: {'OK' if not dep_results.get('missing_files') else 'MISSING FILES'}")
            print(f"UCI Protocol: {'OK' if uci_results.get('success') else 'FAILED'}")
            
            if not uci_results.get('success'):
                print(f"Error: {uci_results.get('error', 'Unknown')}")
            
            if uci_results.get('engine_id'):
                print(f"Engine ID: {uci_results['engine_id'][0]}")
            
            if uci_results.get('bestmove'):
                print(f"Best move: {uci_results['bestmove'][0]}")
            
            print("-" * 60)
        else:
            print(f"\n{name}: FILE NOT FOUND ({path})")

if __name__ == "__main__":
    main()
