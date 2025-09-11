#!/usr/bin/env python3
"""
Large-scale engine comparison between RubiChess and Stockfish on 491 weakness-focused positions.
Designed to expose engine evaluation and move selection differences.
"""

import chess
import chess.engine
import chess.pgn
import csv
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class EngineAnalyzer:
    def __init__(self):
        self.rubichess_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\RubiChess-avx2\RubiChess.exe"
        self.stockfish_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
        
        # Analysis settings
        self.depth = 15
        self.time_limit = 10.0  # seconds
        
        # Results storage
        self.results = []
        self.stats = {
            'total_positions': 0,
            'rubichess_successes': 0,
            'stockfish_successes': 0,
            'move_agreements': 0,
            'large_eval_differences': 0,
            'rubichess_failures': [],
            'stockfish_failures': []
        }

    def analyze_position_with_engine(self, board: chess.Board, engine_path: str, engine_name: str) -> Optional[Dict]:
        """Analyze a single position with specified engine."""
        try:
            with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
                # Set hash size for better performance
                try:
                    engine.configure({"Hash": 256})
                except:
                    pass
                
                # Analyze position
                info = engine.analyse(
                    board, 
                    chess.engine.Limit(depth=self.depth, time=self.time_limit)
                )
                
                # Extract results - info is an AnalysisResult object, not a dict
                best_move = None
                if hasattr(info, 'pv') and info.pv:
                    best_move = info.pv[0]
                
                score = getattr(info, 'score', None)
                nodes = getattr(info, 'nodes', 0)
                time_taken = getattr(info, 'time', 0)
                
                # Convert score to centipawns
                eval_cp = None
                if score:
                    if score.is_mate():
                        # Convert mate scores to large centipawn values
                        mate_in = score.mate()
                        if mate_in > 0:
                            eval_cp = 10000 - mate_in * 10
                        else:
                            eval_cp = -10000 - mate_in * 10
                    else:
                        eval_cp = score.relative.score(mate_score=10000)
                
                return {
                    'engine': engine_name,
                    'best_move': str(best_move) if best_move else None,
                    'evaluation_cp': eval_cp,
                    'nodes': nodes,
                    'time': time_taken,
                    'success': True
                }
                
        except Exception as e:
            print(f"    Error with {engine_name}: {str(e)}")
            return {
                'engine': engine_name,
                'best_move': None,
                'evaluation_cp': None,
                'nodes': 0,
                'time': 0,
                'success': False,
                'error': str(e)
            }

    def analyze_position(self, position_num: int, board: chess.Board) -> Dict:
        """Analyze position with both engines."""
        print(f"[{position_num}/491] Analyzing position {position_num}...")
        
        # Analyze with RubiChess
        print("  RubiChess analyzing...")
        rubichess_result = self.analyze_position_with_engine(board, self.rubichess_path, "RubiChess")
        
        if rubichess_result['success']:
            eval_str = f"{rubichess_result['evaluation_cp']:+}cp" if rubichess_result['evaluation_cp'] is not None else "N/A"
            print(f"    RubiChess: {rubichess_result['best_move']} ({eval_str}) - {rubichess_result['time']:.2f}s")
            self.stats['rubichess_successes'] += 1
        else:
            print(f"    RubiChess: Failed")
            self.stats['rubichess_failures'].append(position_num)
        
        # Analyze with Stockfish
        print("  Stockfish analyzing...")
        stockfish_result = self.analyze_position_with_engine(board, self.stockfish_path, "Stockfish")
        
        if stockfish_result['success']:
            eval_str = f"{stockfish_result['evaluation_cp']:+}cp" if stockfish_result['evaluation_cp'] is not None else "N/A"
            print(f"    Stockfish: {stockfish_result['best_move']} ({eval_str}) - {stockfish_result['time']:.2f}s")
            self.stats['stockfish_successes'] += 1
        else:
            print(f"    Stockfish: Failed")
            self.stats['stockfish_failures'].append(position_num)
        
        # Compare results if both succeeded
        comparison_result = self.compare_results(rubichess_result, stockfish_result)
        if comparison_result:
            print(f"    Comparison: {comparison_result}")
        
        # Combine results
        result = {
            'position': position_num,
            'fen': board.fen(),
            'rubichess_move': rubichess_result['best_move'],
            'rubichess_eval': rubichess_result['evaluation_cp'],
            'rubichess_nodes': rubichess_result['nodes'],
            'rubichess_time': rubichess_result['time'],
            'rubichess_success': rubichess_result['success'],
            'stockfish_move': stockfish_result['best_move'],
            'stockfish_eval': stockfish_result['evaluation_cp'],
            'stockfish_nodes': stockfish_result['nodes'],
            'stockfish_time': stockfish_result['time'],
            'stockfish_success': stockfish_result['success']
        }
        
        return result

    def compare_results(self, rubichess_result: Dict, stockfish_result: Dict) -> Optional[str]:
        """Compare results from both engines."""
        if not (rubichess_result['success'] and stockfish_result['success']):
            return None
        
        # Check move agreement
        moves_agree = rubichess_result['best_move'] == stockfish_result['best_move']
        if moves_agree:
            self.stats['move_agreements'] += 1
        
        # Check evaluation difference
        eval_diff = None
        if rubichess_result['evaluation_cp'] is not None and stockfish_result['evaluation_cp'] is not None:
            eval_diff = abs(rubichess_result['evaluation_cp'] - stockfish_result['evaluation_cp'])
            if eval_diff > 100:
                self.stats['large_eval_differences'] += 1
        
        # Format comparison string
        move_status = "AGREE" if moves_agree else "DIFFER"
        if eval_diff is not None:
            return f"{eval_diff:.0f}cp difference, moves {move_status}"
        else:
            return f"moves {move_status}"

    def save_progress(self, filename: str = "large_scale_progress.csv"):
        """Save current progress to CSV file."""
        if not self.results:
            return
        
        print(f"Saving progress to {filename}...")
        
        fieldnames = [
            'position', 'fen', 
            'rubichess_move', 'rubichess_eval', 'rubichess_nodes', 'rubichess_time', 'rubichess_success',
            'stockfish_move', 'stockfish_eval', 'stockfish_nodes', 'stockfish_time', 'stockfish_success'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

    def load_positions_from_pgn(self, filename: str) -> List[Tuple[int, chess.Board]]:
        """Load positions from PGN file."""
        positions = []
        
        print(f"Loading positions from {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            position_num = 1
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                board = game.board()
                if game.headers.get("FEN"):
                    board.set_fen(game.headers["FEN"])
                
                positions.append((position_num, board))
                position_num += 1
        
        print(f"Loaded {len(positions)} positions")
        return positions

    def print_statistics(self):
        """Print current analysis statistics."""
        total = self.stats['total_positions']
        if total == 0:
            return
        
        print("\n" + "="*60)
        print("LARGE-SCALE ANALYSIS STATISTICS")
        print("="*60)
        print(f"Total positions analyzed: {total}")
        print(f"RubiChess successful analyses: {self.stats['rubichess_successes']}/{total} ({100*self.stats['rubichess_successes']/total:.1f}%)")
        print(f"Stockfish successful analyses: {self.stats['stockfish_successes']}/{total} ({100*self.stats['stockfish_successes']/total:.1f}%)")
        
        successful_comparisons = min(self.stats['rubichess_successes'], self.stats['stockfish_successes'])
        if successful_comparisons > 0:
            print(f"\nComparison Statistics:")
            print(f"Successful comparisons: {successful_comparisons}")
            print(f"Move agreement: {self.stats['move_agreements']}/{successful_comparisons} ({100*self.stats['move_agreements']/successful_comparisons:.1f}%)")
            print(f"Positions with >100cp difference: {self.stats['large_eval_differences']}")
        
        if self.stats['rubichess_failures']:
            print(f"\nRubiChess failures on positions: {self.stats['rubichess_failures'][:10]}{'...' if len(self.stats['rubichess_failures']) > 10 else ''}")
        
        if self.stats['stockfish_failures']:
            print(f"Stockfish failures on positions: {self.stats['stockfish_failures'][:10]}{'...' if len(self.stats['stockfish_failures']) > 10 else ''}")

    def run_analysis(self, pgn_filename: str):
        """Run complete analysis on all positions."""
        print("=== LARGE-SCALE ENGINE COMPARISON ===")
        print(f"RubiChess: {self.rubichess_path}")
        print(f"Stockfish: {self.stockfish_path}")
        print(f"Analysis depth: {self.depth}")
        print(f"Time limit: {self.time_limit}s")
        print()
        
        # Load positions
        positions = self.load_positions_from_pgn(pgn_filename)
        self.stats['total_positions'] = len(positions)
        
        # Analyze each position
        for position_num, board in positions:
            try:
                result = self.analyze_position(position_num, board)
                self.results.append(result)
                
                # Save progress every 25 positions
                if position_num % 25 == 0:
                    self.save_progress(f"large_scale_progress_{position_num}.csv")
                    self.print_statistics()
                    print()
                
            except KeyboardInterrupt:
                print("\nAnalysis interrupted by user")
                break
            except Exception as e:
                print(f"Error analyzing position {position_num}: {e}")
                continue
        
        # Final save and statistics
        self.save_progress("large_scale_engine_comparison.csv")
        self.print_statistics()
        
        print("\n" + "="*60)
        print("LARGE-SCALE ANALYSIS COMPLETE")
        print("="*60)
        print(f"Results saved to large_scale_engine_comparison.csv")
        print("Ready for comprehensive weakness analysis!")

def main():
    """Main analysis function."""
    analyzer = EngineAnalyzer()
    analyzer.run_analysis('weakness_test_positions.pgn')

if __name__ == "__main__":
    main()
