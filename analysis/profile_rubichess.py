#!/usr/bin/env python3
"""
Profile RubiChess engine performance to identify bottlenecks and optimization opportunities.
Uses python-chess to communicate with the engine and measure performance metrics.
"""

import chess
import chess.engine
import time
import statistics
import csv
from collections import defaultdict
import threading
import psutil
import os

# Engine path
RUBICHESS_PATH = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\RubiChess-avx2\RubiChess.exe"

def load_test_positions(pgn_file, max_positions=20):
    """Load a subset of test positions for profiling"""
    positions = []
    try:
        with open(pgn_file, 'r') as f:
            import chess.pgn
            count = 0
            while count < max_positions:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                board = game.board()
                for move in game.mainline_moves():
                    board.push(move)
                
                positions.append({
                    'id': count + 1,
                    'fen': board.fen(),
                    'description': f"Position {count + 1}"
                })
                count += 1
    except FileNotFoundError:
        print(f"Error: {pgn_file} not found")
        return []
    
    return positions

def monitor_process_resources(pid, duration, results_dict):
    """Monitor CPU and memory usage of the engine process"""
    try:
        process = psutil.Process(pid)
        cpu_samples = []
        memory_samples = []
        
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_samples.append(cpu_percent)
                memory_samples.append(memory_mb)
                time.sleep(0.1)  # Sample every 100ms
            except psutil.NoSuchProcess:
                break
        
        results_dict['cpu_avg'] = statistics.mean(cpu_samples) if cpu_samples else 0
        results_dict['cpu_max'] = max(cpu_samples) if cpu_samples else 0
        results_dict['memory_avg'] = statistics.mean(memory_samples) if memory_samples else 0
        results_dict['memory_max'] = max(memory_samples) if memory_samples else 0
        
    except Exception as e:
        print(f"Error monitoring process: {e}")
        results_dict['cpu_avg'] = 0
        results_dict['cpu_max'] = 0
        results_dict['memory_avg'] = 0
        results_dict['memory_max'] = 0

def profile_engine_performance(positions, depths=[10, 15, 20], time_limits=[1.0, 3.0, 5.0]):
    """Profile engine performance across different depths and time limits"""
    
    print("Starting RubiChess performance profiling...")
    
    # Initialize engine
    try:
        engine = chess.engine.SimpleEngine.popen_uci(RUBICHESS_PATH)
        print(f"Engine initialized: {engine.id}")
        
        # Get engine process ID for monitoring
        engine_pid = engine.process.pid
        
    except Exception as e:
        print(f"Error initializing engine: {e}")
        return
    
    profile_results = []
    
    # Test different configurations
    test_configs = []
    
    # Depth-based tests
    for depth in depths:
        test_configs.append({
            'type': 'depth',
            'limit': chess.engine.Limit(depth=depth),
            'description': f"Depth {depth}"
        })
    
    # Time-based tests
    for time_limit in time_limits:
        test_configs.append({
            'type': 'time',
            'limit': chess.engine.Limit(time=time_limit),
            'description': f"Time {time_limit}s"
        })
    
    position_count = 0
    total_positions = len(positions) * len(test_configs)
    
    for pos in positions:
        board = chess.Board(pos['fen'])
        
        for config in test_configs:
            position_count += 1
            print(f"Profiling position {pos['id']} with {config['description']} ({position_count}/{total_positions})")
            
            # Prepare resource monitoring
            resource_results = {}
            
            try:
                # Start resource monitoring in background
                monitor_thread = threading.Thread(
                    target=monitor_process_resources,
                    args=(engine_pid, 10.0, resource_results)  # Monitor for up to 10 seconds
                )
                monitor_thread.start()
                
                # Measure engine analysis time
                start_time = time.time()
                result = engine.analyse(board, config['limit'])
                end_time = time.time()
                
                # Wait for monitoring to complete
                monitor_thread.join(timeout=1.0)
                
                # Extract performance metrics
                analysis_time = end_time - start_time
                nodes = result.get('nodes', 0)
                depth_reached = result.get('depth', 0)
                evaluation = result['score'].relative.score(mate_score=10000) if result.get('score') else 0
                best_move = str(result.get('pv', [None])[0]) if result.get('pv') else 'none'
                
                # Calculate nodes per second
                nps = nodes / analysis_time if analysis_time > 0 else 0
                
                profile_results.append({
                    'position_id': pos['id'],
                    'fen': pos['fen'],
                    'test_type': config['type'],
                    'test_description': config['description'],
                    'analysis_time': analysis_time,
                    'nodes': nodes,
                    'depth_reached': depth_reached,
                    'nodes_per_second': nps,
                    'evaluation_cp': evaluation,
                    'best_move': best_move,
                    'cpu_avg': resource_results.get('cpu_avg', 0),
                    'cpu_max': resource_results.get('cpu_max', 0),
                    'memory_avg_mb': resource_results.get('memory_avg', 0),
                    'memory_max_mb': resource_results.get('memory_max', 0)
                })
                
                print(f"  Time: {analysis_time:.2f}s, Nodes: {nodes:,}, NPS: {nps:,.0f}, Depth: {depth_reached}")
                
            except Exception as e:
                print(f"  Error analyzing position: {e}")
                profile_results.append({
                    'position_id': pos['id'],
                    'fen': pos['fen'],
                    'test_type': config['type'],
                    'test_description': config['description'],
                    'analysis_time': 0,
                    'nodes': 0,
                    'depth_reached': 0,
                    'nodes_per_second': 0,
                    'evaluation_cp': 0,
                    'best_move': 'error',
                    'cpu_avg': 0,
                    'cpu_max': 0,
                    'memory_avg_mb': 0,
                    'memory_max_mb': 0
                })
    
    # Close engine
    engine.quit()
    
    # Save results
    save_profiling_results(profile_results)
    analyze_profiling_results(profile_results)
    
    return profile_results

def save_profiling_results(results):
    """Save profiling results to CSV"""
    csv_filename = 'rubichess_profiling.csv'
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'position_id', 'fen', 'test_type', 'test_description',
            'analysis_time', 'nodes', 'depth_reached', 'nodes_per_second',
            'evaluation_cp', 'best_move', 'cpu_avg', 'cpu_max',
            'memory_avg_mb', 'memory_max_mb'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow(result)
    
    print(f"Profiling results saved to {csv_filename}")

def analyze_profiling_results(results):
    """Analyze profiling results and identify performance patterns"""
    
    print("\n=== RubiChess Performance Analysis ===")
    
    # Group results by test type
    depth_results = [r for r in results if r['test_type'] == 'depth']
    time_results = [r for r in results if r['test_type'] == 'time']
    
    # Analyze depth-based performance
    if depth_results:
        print("\n--- Depth-Based Performance ---")
        depth_groups = defaultdict(list)
        for r in depth_results:
            depth_groups[r['test_description']].append(r)
        
        for depth_desc, group in depth_groups.items():
            valid_results = [r for r in group if r['nodes_per_second'] > 0]
            if valid_results:
                avg_nps = statistics.mean([r['nodes_per_second'] for r in valid_results])
                avg_time = statistics.mean([r['analysis_time'] for r in valid_results])
                avg_nodes = statistics.mean([r['nodes'] for r in valid_results])
                avg_cpu = statistics.mean([r['cpu_avg'] for r in valid_results])
                avg_memory = statistics.mean([r['memory_avg_mb'] for r in valid_results])
                
                print(f"{depth_desc}:")
                print(f"  Average NPS: {avg_nps:,.0f}")
                print(f"  Average time: {avg_time:.2f}s")
                print(f"  Average nodes: {avg_nodes:,.0f}")
                print(f"  Average CPU: {avg_cpu:.1f}%")
                print(f"  Average memory: {avg_memory:.1f} MB")
    
    # Analyze time-based performance
    if time_results:
        print("\n--- Time-Based Performance ---")
        time_groups = defaultdict(list)
        for r in time_results:
            time_groups[r['test_description']].append(r)
        
        for time_desc, group in time_groups.items():
            valid_results = [r for r in group if r['nodes_per_second'] > 0]
            if valid_results:
                avg_nps = statistics.mean([r['nodes_per_second'] for r in valid_results])
                avg_depth = statistics.mean([r['depth_reached'] for r in valid_results])
                avg_nodes = statistics.mean([r['nodes'] for r in valid_results])
                avg_cpu = statistics.mean([r['cpu_avg'] for r in valid_results])
                avg_memory = statistics.mean([r['memory_avg_mb'] for r in valid_results])
                
                print(f"{time_desc}:")
                print(f"  Average NPS: {avg_nps:,.0f}")
                print(f"  Average depth: {avg_depth:.1f}")
                print(f"  Average nodes: {avg_nodes:,.0f}")
                print(f"  Average CPU: {avg_cpu:.1f}%")
                print(f"  Average memory: {avg_memory:.1f} MB")
    
    # Overall performance metrics
    valid_results = [r for r in results if r['nodes_per_second'] > 0]
    if valid_results:
        overall_nps = [r['nodes_per_second'] for r in valid_results]
        overall_cpu = [r['cpu_avg'] for r in valid_results]
        overall_memory = [r['memory_avg_mb'] for r in valid_results]
        
        print(f"\n--- Overall Performance Summary ---")
        print(f"Total test runs: {len(results)}")
        print(f"Successful runs: {len(valid_results)}")
        print(f"Average NPS: {statistics.mean(overall_nps):,.0f}")
        print(f"NPS range: {min(overall_nps):,.0f} - {max(overall_nps):,.0f}")
        print(f"Average CPU usage: {statistics.mean(overall_cpu):.1f}%")
        print(f"Average memory usage: {statistics.mean(overall_memory):.1f} MB")
    
    # Create performance summary report
    create_performance_report(results)

def create_performance_report(results):
    """Create markdown performance report"""
    
    with open('rubichess_performance_report.md', 'w') as f:
        f.write("# RubiChess Performance Profiling Report\n\n")
        
        valid_results = [r for r in results if r['nodes_per_second'] > 0]
        
        f.write("## Executive Summary\n")
        f.write(f"- Total test configurations: {len(set(r['test_description'] for r in results))}\n")
        f.write(f"- Total positions tested: {len(set(r['position_id'] for r in results))}\n")
        f.write(f"- Successful analyses: {len(valid_results)}/{len(results)}\n")
        
        if valid_results:
            avg_nps = statistics.mean([r['nodes_per_second'] for r in valid_results])
            avg_cpu = statistics.mean([r['cpu_avg'] for r in valid_results])
            avg_memory = statistics.mean([r['memory_avg_mb'] for r in valid_results])
            
            f.write(f"- Average performance: {avg_nps:,.0f} nodes/second\n")
            f.write(f"- Average CPU usage: {avg_cpu:.1f}%\n")
            f.write(f"- Average memory usage: {avg_memory:.1f} MB\n\n")
        
        f.write("## Performance Bottlenecks Identified\n")
        f.write("Based on the profiling data, potential optimization areas include:\n\n")
        
        # Identify slow positions
        if valid_results:
            slow_threshold = statistics.mean([r['nodes_per_second'] for r in valid_results]) * 0.7
            slow_results = [r for r in valid_results if r['nodes_per_second'] < slow_threshold]
            
            if slow_results:
                f.write(f"### Slow Analysis Positions ({len(slow_results)} positions)\n")
                f.write("Positions that analyzed significantly slower than average:\n\n")
                for r in sorted(slow_results, key=lambda x: x['nodes_per_second'])[:5]:
                    f.write(f"- Position {r['position_id']}: {r['nodes_per_second']:,.0f} NPS ({r['test_description']})\n")
                f.write("\n")
        
        f.write("### Recommended Optimizations\n")
        f.write("1. **Search Algorithm**: Focus on positions with low NPS\n")
        f.write("2. **Evaluation Function**: Profile evaluation-heavy positions\n")
        f.write("3. **Memory Management**: Monitor memory usage patterns\n")
        f.write("4. **Move Generation**: Optimize for tactical positions\n\n")
        
        f.write("## Detailed Results\n")
        f.write("See `rubichess_profiling.csv` for complete performance data.\n")

def main():
    """Main profiling function"""
    print("RubiChess Performance Profiler")
    print("=" * 40)
    
    # Load test positions (use subset for profiling)
    positions = load_test_positions("positions.pgn", max_positions=10)
    if not positions:
        print("No positions loaded. Exiting.")
        return
    
    print(f"Loaded {len(positions)} positions for profiling")
    
    # Run profiling with different configurations
    results = profile_engine_performance(
        positions,
        depths=[10, 15],  # Reduced for faster profiling
        time_limits=[2.0, 5.0]  # Reduced for faster profiling
    )
    
    print("\nProfiling complete!")
    print("Results saved to rubichess_profiling.csv and rubichess_performance_report.md")

if __name__ == "__main__":
    main()
