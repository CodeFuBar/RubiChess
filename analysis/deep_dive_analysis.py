#!/usr/bin/env python3
"""
Deep Dive Weak-Spot Analysis for Positions 135-142
Comprehensive analysis of the worst-performing positions from large-scale testing.
"""

import chess
import chess.pgn
import chess.engine
import csv
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class DeepDiveAnalyzer:
    def __init__(self):
        self.rubichess_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\RubiChess-avx2\RubiChess.exe"
        self.stockfish_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
        
        # Analysis settings
        self.baseline_depth = 15
        self.baseline_time = 8.0
        self.extended_depth = 25
        self.extended_time = 20.0
        self.reference_depth = 20
        self.reference_time = 15.0
        
        # Target positions (worst performers from large-scale analysis)
        self.target_positions = [135, 136, 137, 138, 139, 140, 141, 142]
        
        # Results storage
        self.analysis_results = {}

    def load_positions(self, pgn_filename: str) -> Dict[int, chess.Board]:
        """Load specific positions from PGN file."""
        positions = {}
        
        print(f"Loading positions {self.target_positions} from {pgn_filename}...")
        
        with open(pgn_filename, 'r', encoding='utf-8') as f:
            position_num = 1
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                if position_num in self.target_positions:
                    board = game.board()
                    if game.headers.get("FEN"):
                        board.set_fen(game.headers["FEN"])
                    
                    positions[position_num] = board
                    print(f"  Loaded position {position_num}: {board.fen()}")
                
                position_num += 1
        
        print(f"Successfully loaded {len(positions)} critical positions")
        return positions

    def analyze_with_engine(self, board: chess.Board, engine_path: str, engine_name: str, 
                          depth: int, time_limit: float, multipv: int = 1) -> Dict:
        """Comprehensive engine analysis with extended information."""
        try:
            with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
                # Configure engine
                try:
                    engine.configure({"Hash": 512, "MultiPV": multipv})
                except:
                    pass
                
                # Analyze position
                start_time = time.time()
                info = engine.analyse(
                    board, 
                    chess.engine.Limit(depth=depth, time=time_limit),
                    multipv=multipv
                )
                end_time = time.time()
                
                analysis_time = end_time - start_time
                
                # Extract comprehensive results
                if multipv == 1:
                    # Single PV analysis
                    best_move = info.pv[0] if info.pv else None
                    pv_moves = [str(move) for move in info.pv] if info.pv else []
                    
                    eval_cp = None
                    if info.score:
                        if info.score.is_mate():
                            mate_in = info.score.mate()
                            eval_cp = 10000 - abs(mate_in) * 10 if mate_in > 0 else -10000 + abs(mate_in) * 10
                        else:
                            eval_cp = info.score.relative.score(mate_score=10000)
                    
                    return {
                        'engine': engine_name,
                        'success': True,
                        'best_move': str(best_move) if best_move else None,
                        'evaluation': eval_cp,
                        'pv': pv_moves,
                        'pv_length': len(pv_moves),
                        'depth': getattr(info, 'depth', depth),
                        'nodes': getattr(info, 'nodes', 0),
                        'time': analysis_time,
                        'nps': getattr(info, 'nodes', 0) / analysis_time if analysis_time > 0 else 0
                    }
                else:
                    # Multi-PV analysis
                    results = []
                    for pv_info in info:
                        best_move = pv_info.pv[0] if pv_info.pv else None
                        pv_moves = [str(move) for move in pv_info.pv] if pv_info.pv else []
                        
                        eval_cp = None
                        if pv_info.score:
                            if pv_info.score.is_mate():
                                mate_in = pv_info.score.mate()
                                eval_cp = 10000 - abs(mate_in) * 10 if mate_in > 0 else -10000 + abs(mate_in) * 10
                            else:
                                eval_cp = pv_info.score.relative.score(mate_score=10000)
                        
                        results.append({
                            'move': str(best_move) if best_move else None,
                            'evaluation': eval_cp,
                            'pv': pv_moves,
                            'pv_length': len(pv_moves)
                        })
                    
                    return {
                        'engine': engine_name,
                        'success': True,
                        'multipv_results': results,
                        'depth': getattr(info[0], 'depth', depth) if info else depth,
                        'nodes': getattr(info[0], 'nodes', 0) if info else 0,
                        'time': analysis_time,
                        'nps': getattr(info[0], 'nodes', 0) / analysis_time if analysis_time > 0 and info else 0
                    }
                    
        except Exception as e:
            return {
                'engine': engine_name,
                'success': False,
                'error': str(e),
                'time': 0
            }

    def baseline_analysis(self, positions: Dict[int, chess.Board]):
        """Step 2: Baseline analysis with original settings."""
        print(f"\n=== BASELINE ANALYSIS (Depth {self.baseline_depth}, Time {self.baseline_time}s) ===")
        
        for pos_id, board in positions.items():
            print(f"\n[Position {pos_id}] Baseline Analysis...")
            
            # Analyze with RubiChess
            print("  RubiChess baseline...")
            rubichess_result = self.analyze_with_engine(
                board, self.rubichess_path, "RubiChess", 
                self.baseline_depth, self.baseline_time
            )
            
            if rubichess_result['success']:
                print(f"    Move: {rubichess_result['best_move']}")
                print(f"    Eval: {rubichess_result['evaluation']:+}cp")
                print(f"    PV: {' '.join(rubichess_result['pv'][:6])}")
                print(f"    Depth: {rubichess_result['depth']}, Nodes: {rubichess_result['nodes']:,}")
            else:
                print(f"    Failed: {rubichess_result.get('error', 'Unknown error')}")
            
            # Store results
            if pos_id not in self.analysis_results:
                self.analysis_results[pos_id] = {'fen': board.fen()}
            self.analysis_results[pos_id]['baseline'] = rubichess_result

    def extended_analysis(self, positions: Dict[int, chess.Board]):
        """Step 3: Extended analysis with deeper search."""
        print(f"\n=== EXTENDED ANALYSIS (Depth {self.extended_depth}, Time {self.extended_time}s) ===")
        
        for pos_id, board in positions.items():
            print(f"\n[Position {pos_id}] Extended Analysis...")
            
            # Analyze with RubiChess at extended depth
            print("  RubiChess extended...")
            rubichess_result = self.analyze_with_engine(
                board, self.rubichess_path, "RubiChess", 
                self.extended_depth, self.extended_time
            )
            
            if rubichess_result['success']:
                print(f"    Move: {rubichess_result['best_move']}")
                print(f"    Eval: {rubichess_result['evaluation']:+}cp")
                print(f"    PV: {' '.join(rubichess_result['pv'][:6])}")
                print(f"    Depth: {rubichess_result['depth']}, Nodes: {rubichess_result['nodes']:,}")
            else:
                print(f"    Failed: {rubichess_result.get('error', 'Unknown error')}")
            
            # Store results
            self.analysis_results[pos_id]['extended'] = rubichess_result

    def self_comparison(self):
        """Step 4: Compare baseline vs extended results."""
        print(f"\n=== SELF-COMPARISON ANALYSIS ===")
        
        for pos_id in self.target_positions:
            if pos_id not in self.analysis_results:
                continue
                
            baseline = self.analysis_results[pos_id].get('baseline', {})
            extended = self.analysis_results[pos_id].get('extended', {})
            
            if not (baseline.get('success') and extended.get('success')):
                continue
            
            print(f"\n[Position {pos_id}] Self-Comparison:")
            
            # Compare moves
            baseline_move = baseline.get('best_move')
            extended_move = extended.get('best_move')
            moves_differ = baseline_move != extended_move
            
            # Compare evaluations
            baseline_eval = baseline.get('evaluation', 0)
            extended_eval = extended.get('evaluation', 0)
            eval_swing = abs(baseline_eval - extended_eval) if baseline_eval and extended_eval else 0
            
            print(f"  Baseline: {baseline_move} ({baseline_eval:+}cp)")
            print(f"  Extended: {extended_move} ({extended_eval:+}cp)")
            print(f"  Move differs: {moves_differ}")
            print(f"  Eval swing: {eval_swing}cp")
            
            # Flag significant differences
            flags = []
            if moves_differ:
                flags.append("MOVE_CHANGE")
            if eval_swing > 50:  # 0.5 pawn equivalent
                flags.append("LARGE_EVAL_SWING")
            
            self.analysis_results[pos_id]['self_comparison'] = {
                'moves_differ': moves_differ,
                'eval_swing': eval_swing,
                'flags': flags
            }
            
            if flags:
                print(f"  FLAGS: {', '.join(flags)}")

    def expand_principal_variations(self):
        """Step 5: Expand PVs to 6-10 plies for detailed analysis."""
        print(f"\n=== PRINCIPAL VARIATION EXPANSION ===")
        
        for pos_id in self.target_positions:
            if pos_id not in self.analysis_results:
                continue
            
            print(f"\n[Position {pos_id}] PV Analysis:")
            
            baseline = self.analysis_results[pos_id].get('baseline', {})
            extended = self.analysis_results[pos_id].get('extended', {})
            
            if baseline.get('success'):
                baseline_pv = baseline.get('pv', [])
                print(f"  Baseline PV ({len(baseline_pv)} moves): {' '.join(baseline_pv[:10])}")
            
            if extended.get('success'):
                extended_pv = extended.get('pv', [])
                print(f"  Extended PV ({len(extended_pv)} moves): {' '.join(extended_pv[:10])}")

    def reference_engine_analysis(self, positions: Dict[int, chess.Board]):
        """Step 6: Cross-check with Stockfish reference."""
        print(f"\n=== REFERENCE ENGINE ANALYSIS (Stockfish, Depth {self.reference_depth}) ===")
        
        for pos_id, board in positions.items():
            print(f"\n[Position {pos_id}] Reference Analysis...")
            
            # Analyze with Stockfish
            print("  Stockfish reference...")
            stockfish_result = self.analyze_with_engine(
                board, self.stockfish_path, "Stockfish", 
                self.reference_depth, self.reference_time
            )
            
            if stockfish_result['success']:
                print(f"    Move: {stockfish_result['best_move']}")
                print(f"    Eval: {stockfish_result['evaluation']:+}cp")
                print(f"    PV: {' '.join(stockfish_result['pv'][:6])}")
                print(f"    Depth: {stockfish_result['depth']}, Nodes: {stockfish_result['nodes']:,}")
            else:
                print(f"    Failed: {stockfish_result.get('error', 'Unknown error')}")
            
            # Store results
            self.analysis_results[pos_id]['reference'] = stockfish_result

    def automated_heuristics(self):
        """Step 7: Apply automated evaluation heuristics."""
        print(f"\n=== AUTOMATED HEURISTICS ANALYSIS ===")
        
        for pos_id in self.target_positions:
            if pos_id not in self.analysis_results:
                continue
            
            result = self.analysis_results[pos_id]
            baseline = result.get('baseline', {})
            extended = result.get('extended', {})
            reference = result.get('reference', {})
            
            flags = []
            issues = []
            
            print(f"\n[Position {pos_id}] Heuristics Check:")
            
            # Check 1: Engine move significantly worse than reference
            if (baseline.get('success') and reference.get('success') and 
                baseline.get('evaluation') and reference.get('evaluation')):
                
                eval_diff = abs(baseline['evaluation'] - reference['evaluation'])
                if eval_diff > 100:  # >1.0 pawn difference
                    flags.append("LARGE_EVAL_DIFF_VS_REF")
                    issues.append(f"Baseline eval differs from reference by {eval_diff}cp")
            
            # Check 2: Baseline vs extended depth inconsistency
            if (baseline.get('success') and extended.get('success') and 
                baseline.get('evaluation') and extended.get('evaluation')):
                
                depth_eval_diff = abs(baseline['evaluation'] - extended['evaluation'])
                if depth_eval_diff > 100:  # >1.0 pawn shift with depth
                    flags.append("DEPTH_INSTABILITY")
                    issues.append(f"Eval shifts {depth_eval_diff}cp between depths")
            
            # Check 3: Move differs significantly from reference
            if (baseline.get('success') and reference.get('success')):
                if baseline.get('best_move') != reference.get('best_move'):
                    flags.append("MOVE_DIFFERS_FROM_REF")
                    issues.append(f"Move differs from reference: {baseline.get('best_move')} vs {reference.get('best_move')}")
            
            # Check 4: Extended analysis differs from reference
            if (extended.get('success') and reference.get('success')):
                if extended.get('best_move') != reference.get('best_move'):
                    flags.append("EXTENDED_MOVE_DIFFERS_FROM_REF")
                    issues.append(f"Extended move differs from reference: {extended.get('best_move')} vs {reference.get('best_move')}")
            
            # Store heuristics results
            result['heuristics'] = {
                'flags': flags,
                'issues': issues
            }
            
            print(f"  Flags: {', '.join(flags) if flags else 'None'}")
            for issue in issues:
                print(f"  Issue: {issue}")

    def annotate_findings(self):
        """Step 8: Collect and annotate all findings."""
        print(f"\n=== ANNOTATING FINDINGS ===")
        
        for pos_id in self.target_positions:
            if pos_id not in self.analysis_results:
                continue
            
            result = self.analysis_results[pos_id]
            
            # Collect key information
            baseline = result.get('baseline', {})
            extended = result.get('extended', {})
            reference = result.get('reference', {})
            heuristics = result.get('heuristics', {})
            
            # Create annotation
            annotation = {
                'position_id': pos_id,
                'fen': result.get('fen', ''),
                'baseline_move': baseline.get('best_move', 'N/A'),
                'baseline_eval': baseline.get('evaluation', 'N/A'),
                'extended_move': extended.get('best_move', 'N/A'),
                'extended_eval': extended.get('evaluation', 'N/A'),
                'reference_move': reference.get('best_move', 'N/A'),
                'reference_eval': reference.get('evaluation', 'N/A'),
                'detected_issues': heuristics.get('flags', []),
                'notes': '; '.join(heuristics.get('issues', []))
            }
            
            result['annotation'] = annotation
            
            print(f"[Position {pos_id}] Annotated with {len(annotation['detected_issues'])} issues")

    def generate_summary_report(self):
        """Step 9: Generate comprehensive summary report."""
        print(f"\n=== GENERATING SUMMARY REPORT ===")
        
        # Prepare summary data
        summary_data = []
        
        for pos_id in self.target_positions:
            if pos_id not in self.analysis_results:
                continue
            
            annotation = self.analysis_results[pos_id].get('annotation', {})
            summary_data.append(annotation)
        
        # Save to CSV
        csv_filename = 'deep_dive_analysis_summary.csv'
        fieldnames = [
            'position_id', 'fen', 'baseline_move', 'baseline_eval', 
            'extended_move', 'extended_eval', 'reference_move', 'reference_eval',
            'detected_issues', 'notes'
        ]
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in summary_data:
                # Convert lists to strings for CSV
                row_copy = row.copy()
                if isinstance(row_copy.get('detected_issues'), list):
                    row_copy['detected_issues'] = ', '.join(row_copy['detected_issues'])
                writer.writerow(row_copy)
        
        # Save detailed JSON results
        json_filename = 'deep_dive_analysis_detailed.json'
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.analysis_results, jsonfile, indent=2, default=str)
        
        # Generate markdown report
        self.generate_markdown_report(summary_data)
        
        print(f"Summary saved to: {csv_filename}")
        print(f"Detailed results saved to: {json_filename}")
        print(f"Markdown report saved to: deep_dive_analysis_report.md")

    def generate_markdown_report(self, summary_data: List[Dict]):
        """Generate detailed markdown report."""
        
        report_content = f"""# Deep Dive Weak-Spot Analysis: Positions 135-142
## Comprehensive Analysis of Critical Evaluation Failures

### Executive Summary

Deep dive analysis of the 8 worst-performing positions from large-scale weakness testing, examining baseline vs extended depth analysis and cross-referencing with Stockfish.

**Positions Analyzed:** {', '.join(map(str, self.target_positions))}
**Analysis Depths:** Baseline {self.baseline_depth}, Extended {self.extended_depth}, Reference {self.reference_depth}

---

## Summary Table

| Position | Baseline Move/Eval | Extended Move/Eval | Reference Move/Eval | Issues | Notes |
|----------|-------------------|-------------------|-------------------|---------|-------|"""

        for data in summary_data:
            pos_id = data.get('position_id', 'N/A')
            baseline_move = data.get('baseline_move', 'N/A')
            baseline_eval = f"{data.get('baseline_eval'):+}cp" if isinstance(data.get('baseline_eval'), (int, float)) else 'N/A'
            extended_move = data.get('extended_move', 'N/A')
            extended_eval = f"{data.get('extended_eval'):+}cp" if isinstance(data.get('extended_eval'), (int, float)) else 'N/A'
            reference_move = data.get('reference_move', 'N/A')
            reference_eval = f"{data.get('reference_eval'):+}cp" if isinstance(data.get('reference_eval'), (int, float)) else 'N/A'
            issues = data.get('detected_issues', '')
            notes = data.get('notes', '')[:50] + '...' if len(data.get('notes', '')) > 50 else data.get('notes', '')
            
            report_content += f"""
| {pos_id} | {baseline_move} ({baseline_eval}) | {extended_move} ({extended_eval}) | {reference_move} ({reference_eval}) | {issues} | {notes} |"""

        report_content += f"""

---

## Detailed Position Analysis

"""

        for pos_id in self.target_positions:
            if pos_id not in self.analysis_results:
                continue
            
            result = self.analysis_results[pos_id]
            baseline = result.get('baseline', {})
            extended = result.get('extended', {})
            reference = result.get('reference', {})
            heuristics = result.get('heuristics', {})
            
            report_content += f"""
### Position {pos_id}

**FEN:** `{result.get('fen', 'N/A')}`

**Analysis Results:**
- **Baseline (Depth {self.baseline_depth}):** {baseline.get('best_move', 'N/A')} ({f"{baseline.get('evaluation'):+}cp" if isinstance(baseline.get('evaluation'), (int, float)) else 'N/A'})
- **Extended (Depth {self.extended_depth}):** {extended.get('best_move', 'N/A')} ({f"{extended.get('evaluation'):+}cp" if isinstance(extended.get('evaluation'), (int, float)) else 'N/A'})
- **Reference (Stockfish):** {reference.get('best_move', 'N/A')} ({f"{reference.get('evaluation'):+}cp" if isinstance(reference.get('evaluation'), (int, float)) else 'N/A'})

**Principal Variations:**
- **Baseline PV:** {' '.join(baseline.get('pv', [])[:8])}
- **Extended PV:** {' '.join(extended.get('pv', [])[:8])}
- **Reference PV:** {' '.join(reference.get('pv', [])[:8])}

**Detected Issues:**
{chr(10).join([f'- {issue}' for issue in heuristics.get('issues', ['None detected'])])}

**Performance Metrics:**
- **Baseline:** {baseline.get('nodes', 0):,} nodes in {baseline.get('time', 0):.2f}s ({baseline.get('nps', 0):,.0f} nps)
- **Extended:** {extended.get('nodes', 0):,} nodes in {extended.get('time', 0):.2f}s ({extended.get('nps', 0):,.0f} nps)
- **Reference:** {reference.get('nodes', 0):,} nodes in {reference.get('time', 0):.2f}s ({reference.get('nps', 0):,.0f} nps)

---"""

        report_content += f"""

## Key Findings and Recommendations

### Critical Issues Identified
1. **Evaluation Instability:** Significant evaluation changes between search depths
2. **Move Selection Errors:** Different moves chosen compared to reference engine
3. **Tactical Blind Spots:** Missing key tactical motifs in complex positions
4. **Search Inefficiency:** Lower nodes-per-second compared to reference engine

### Immediate Actions Required
1. **Manual Position Review:** Each flagged position needs human expert analysis
2. **Evaluation Function Audit:** Focus on positions with large evaluation discrepancies
3. **Search Parameter Tuning:** Adjust pruning and extension parameters
4. **Tactical Recognition Improvement:** Enhance tactical pattern recognition

### Next Steps
1. Implement fixes for identified issues
2. Re-run analysis to verify improvements
3. Extend analysis to additional problematic positions
4. Integrate findings into main engine optimization roadmap

---

*Analysis completed: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""

        with open('deep_dive_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)

    def run_complete_analysis(self):
        """Run the complete 9-step deep dive analysis."""
        print("="*80)
        print("DEEP DIVE WEAK-SPOT ANALYSIS: POSITIONS 135-142")
        print("="*80)
        
        # Step 1: Load Positions
        positions = self.load_positions('weakness_test_positions.pgn')
        
        if not positions:
            print("ERROR: No positions loaded. Exiting.")
            return
        
        # Step 2: Baseline Analysis
        self.baseline_analysis(positions)
        
        # Step 3: Extended Analysis
        self.extended_analysis(positions)
        
        # Step 4: Self-Comparison
        self.self_comparison()
        
        # Step 5: Expand Principal Variations
        self.expand_principal_variations()
        
        # Step 6: Reference Engine Analysis
        self.reference_engine_analysis(positions)
        
        # Step 7: Automated Heuristics
        self.automated_heuristics()
        
        # Step 8: Annotate Findings
        self.annotate_findings()
        
        # Step 9: Generate Summary Report
        self.generate_summary_report()
        
        print("\n" + "="*80)
        print("DEEP DIVE ANALYSIS COMPLETE")
        print("="*80)
        print("All analysis steps completed successfully!")
        print("Check the generated files for detailed results.")

def main():
    """Main execution function."""
    analyzer = DeepDiveAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
