#!/usr/bin/env python3
"""
Evaluation Component Comparison Tool for Phase 2

This tool performs detailed component-by-component comparison between RubiChess
and Stockfish evaluations to identify specific parameter discrepancies.

Uses:
- RubiChess's traceEvalOut() system for detailed evaluation breakdown
- Stockfish's 'eval' command for NNUE component analysis
"""

import subprocess
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import json


@dataclass
class RubiChessTrace:
    """Stores RubiChess evaluation trace components"""
    material: Tuple[int, int]  # (MG, EG)
    minors: Tuple[int, int]
    rooks: Tuple[int, int]
    pawns: Tuple[int, int]
    passers: Tuple[int, int]
    mobility: Tuple[int, int]
    threats: Tuple[int, int]
    king_attacks: Tuple[int, int]
    complexity: Tuple[int, int]
    tempo: Tuple[int, int]
    total: Tuple[int, int]
    final_eval: int  # Centipawns


@dataclass
class StockfishEval:
    """Stores Stockfish evaluation components"""
    nnue_eval: float
    final_eval: float
    material_psqt: float
    positional: float
    bucket_used: int
    piece_values: Dict[str, float]


@dataclass
class ComparisonResult:
    """Stores comparison results for a position"""
    fen: str
    position_id: int
    rubichess: RubiChessTrace
    stockfish: StockfishEval
    eval_difference: float  # RubiChess - Stockfish (in centipawns)
    component_discrepancies: Dict[str, float]
    recommendations: List[str]


class EvaluationComparator:
    def __init__(self):
        self.rubichess_path = r"..\RubiChess\x64\Release\RubiChess.exe"
        self.stockfish_path = r"C:\Program Files (x86)\Common Files\ChessBase\Engines.uci\Stockfish_25090605_x64_avx2\stockfish_25090605_x64_avx2.exe"
        
        # Target positions for analysis
        self.target_positions = {
            60: "r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/3PbN2/PPP2PPP/RNBQ1RK1 w kq - 1 6",
            98: "8/8/2k5/5p2/6p1/2K5/3P4/8 b - - 1 1",
            103: "8/8/1p1k4/3p4/3P4/1P6/4K3/8 b - - 1 1"
        }
    
    def run_rubichess_trace(self, fen: str) -> Optional[RubiChessTrace]:
        """
        Run RubiChess search to get actual UCI-scaled evaluation
        Uses search instead of eval command for accurate centipawn values
        """
        try:
            # Get the directory where RubiChess is located (for NNUE file access)
            import os
            rubichess_dir = os.path.dirname(os.path.abspath(self.rubichess_path))
            
            process = subprocess.Popen(
                [self.rubichess_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=rubichess_dir,  # Run from the Release folder so NNUE file is found
                bufsize=1
            )
            
            # Send commands with delays to ensure proper processing
            def send_cmd(cmd, delay=0.1):
                process.stdin.write(cmd + "\n")
                process.stdin.flush()
                time.sleep(delay)
            
            send_cmd("uci", 0.3)
            send_cmd("isready", 0.2)
            send_cmd(f"position fen {fen}", 0.1)
            send_cmd("go depth 12", 5)  # Search to depth 12, wait up to 5 seconds
            send_cmd("quit", 0.1)
            
            stdout, stderr = process.communicate(timeout=10)
            
            # Split output into lines and parse
            output_lines = [line.strip() for line in stdout.split('\n') if line.strip()]
            
            # Extract the final evaluation from search output
            final_eval = 0
            for line in reversed(output_lines):
                if 'score cp' in line:
                    match = re.search(r'score cp ([+-]?\d+)', line)
                    if match:
                        final_eval = int(match.group(1))
                        break
            
            # Return trace with search-based evaluation
            # NNUE doesn't provide component breakdown, so we just have the total
            return RubiChessTrace(
                material=(final_eval, final_eval),  # Store total in material for reference
                minors=(0, 0),
                rooks=(0, 0),
                pawns=(0, 0),
                passers=(0, 0),
                mobility=(0, 0),
                threats=(0, 0),
                king_attacks=(0, 0),
                complexity=(0, 0),
                tempo=(0, 0),
                total=(final_eval, final_eval),
                final_eval=final_eval
            )
            
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] RubiChess took too long")
            process.kill()
            process.communicate()
            return None
        except Exception as e:
            print(f"Error running RubiChess: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_rubichess_trace(self, lines: List[str]) -> Optional[RubiChessTrace]:
        """Parse RubiChess trace evaluation output - handles both NNUE and classic formats"""
        
        def extract_component_values(line: str) -> Tuple[int, int]:
            """Extract total MG and EG values from a trace line (in centipawns)"""
            # Line format: "     Material | +0.50 +0.30 | -0.45 -0.28 | +0.05 +0.02"
            # Values are in pawns, convert to centipawns
            # We want the last two values (Total MG, Total EG)
            parts = line.split('|')
            if len(parts) >= 4:
                total_part = parts[-1].strip()
                values = re.findall(r'([+-]?\d+\.\d+)', total_part)
                if len(values) >= 2:
                    mg = int(float(values[0]) * 100)  # Convert pawns to centipawns
                    eg = int(float(values[1]) * 100)  # Convert pawns to centipawns
                    return (mg, eg)
            return (0, 0)
        
        def extract_cp_value(line: str) -> int:
            """Extract centipawn value from Resulting line"""
            # Line format: "    Resulting |  +0.20" (in pawns)
            match = re.search(r'([+-]?\d+\.\d+)', line.split('|')[-1])
            if match:
                return int(float(match.group(1)) * 100)  # Convert pawns to centipawns
            return 0
        
        def extract_nnue_value(line: str) -> int:
            """Extract value from NNUE output line"""
            # Line format: "Raw NNUE eval:  193273" or "Total:          175173"
            match = re.search(r':\s*([+-]?\d+)', line)
            if match:
                # NNUE values are in internal units, divide by 1000 to get centipawns approx
                return int(int(match.group(1)) / 1000)
            return 0
        
        # Initialize components
        material = (0, 0)
        minors = (0, 0)
        rooks = (0, 0)
        pawns = (0, 0)
        passers = (0, 0)
        mobility = (0, 0)
        threats = (0, 0)
        king_attacks = (0, 0)
        complexity = (0, 0)
        tempo = (0, 0)
        total = (0, 0)
        final_eval = 0
        is_nnue = False
        nnue_raw = 0
        nnue_scaled = 0
        nnue_tempo = 0
        
        # Parse each line
        for line in lines:
            # Check for NNUE format
            if "Raw NNUE eval:" in line:
                is_nnue = True
                nnue_raw = extract_nnue_value(line)
            elif "Phased scaled:" in line:
                nnue_scaled = extract_nnue_value(line)
            elif "Tempo:" in line and is_nnue:
                nnue_tempo = extract_nnue_value(line)
            elif "Total:" in line and is_nnue:
                final_eval = extract_nnue_value(line)
            # Classic format parsing
            elif "Material |" in line:
                material = extract_component_values(line)
            elif "Minors |" in line:
                minors = extract_component_values(line)
            elif "Rooks |" in line:
                rooks = extract_component_values(line)
            elif "Pawns |" in line:
                pawns = extract_component_values(line)
            elif "Passers |" in line:
                passers = extract_component_values(line)
            elif "Mobility |" in line:
                mobility = extract_component_values(line)
            elif "Threats |" in line:
                threats = extract_component_values(line)
            elif "King attacks |" in line:
                king_attacks = extract_component_values(line)
            elif "Complexity |" in line:
                complexity = extract_component_values(line)
            elif "Tempo |" in line and not is_nnue:
                tempo = extract_component_values(line)
            elif "Total |" in line and "Ph=" in line:
                total = extract_component_values(line)
            elif "Resulting |" in line:
                final_eval = extract_cp_value(line)
        
        # For NNUE mode, store raw and scaled values in material/total for reference
        if is_nnue:
            material = (nnue_raw, nnue_raw)  # Store NNUE raw eval
            total = (nnue_scaled, nnue_scaled)  # Store scaled eval
            tempo = (nnue_tempo, nnue_tempo)
        
        return RubiChessTrace(
            material=material,
            minors=minors,
            rooks=rooks,
            pawns=pawns,
            passers=passers,
            mobility=mobility,
            threats=threats,
            king_attacks=king_attacks,
            complexity=complexity,
            tempo=tempo,
            total=total,
            final_eval=final_eval
        )
    
    def run_stockfish_eval(self, fen: str) -> Optional[StockfishEval]:
        """Run Stockfish eval command to get detailed evaluation breakdown"""
        try:
            process = subprocess.Popen(
                [self.stockfish_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Initialize UCI
            process.stdin.write("uci\n")
            process.stdin.flush()
            
            # Wait for uciok
            while True:
                line = process.stdout.readline().strip()
                if line == "uciok":
                    break
            
            # Set position
            process.stdin.write(f"position fen {fen}\n")
            process.stdin.flush()
            time.sleep(0.1)
            
            # Request eval command
            process.stdin.write("eval\n")
            process.stdin.flush()
            
            # Collect eval output
            eval_lines = []
            start_time = time.time()
            while time.time() - start_time < 3:  # 3 second timeout
                line = process.stdout.readline().strip()
                if line:
                    eval_lines.append(line)
                if "Final evaluation" in line or "Total evaluation" in line:
                    break
            
            process.stdin.write("quit\n")
            process.stdin.flush()
            process.terminate()
            
            # Parse eval output
            return self._parse_stockfish_eval(eval_lines)
            
        except Exception as e:
            print(f"Error running Stockfish eval: {e}")
            return None
    
    def _parse_stockfish_eval(self, lines: List[str]) -> Optional[StockfishEval]:
        """Parse Stockfish eval command output"""
        nnue_eval = 0.0
        final_eval = 0.0
        material_psqt = 0.0
        positional = 0.0
        bucket_used = -1
        piece_values = {}
        
        for line in lines:
            # Parse NNUE evaluation
            if "NNUE evaluation" in line:
                match = re.search(r'NNUE evaluation\s+([+-]?\d+\.\d+)', line)
                if match:
                    nnue_eval = float(match.group(1))
            
            # Parse Final evaluation
            if "Final evaluation" in line:
                match = re.search(r'Final evaluation\s+([+-]?\d+\.\d+)', line)
                if match:
                    final_eval = float(match.group(1))
            
            # Parse bucket information
            if "<-- this bucket is used" in line:
                match = re.search(r'\|\s*(\d+)\s+\|', line)
                if match:
                    bucket_used = int(match.group(1))
                # Extract material and positional from bucket line
                values = re.findall(r'([+-])\s+(\d+\.\d+)', line)
                if len(values) >= 3:
                    material_psqt = float(values[0][1]) if values[0][0] == '+' else -float(values[0][1])
                    positional = float(values[1][1]) if values[1][0] == '+' else -float(values[1][1])
        
        return StockfishEval(
            nnue_eval=nnue_eval,
            final_eval=final_eval,
            material_psqt=material_psqt,
            positional=positional,
            bucket_used=bucket_used,
            piece_values=piece_values
        )
    
    def compare_evaluations(self, position_id: int, fen: str) -> ComparisonResult:
        """Compare RubiChess and Stockfish evaluations for a position"""
        print(f"\n{'='*80}")
        print(f"Analyzing Position {position_id}")
        print(f"FEN: {fen}")
        print(f"{'='*80}")
        
        # Get RubiChess evaluation
        print("\n[1/2] Running RubiChess evaluation...")
        rubichess_trace = self.run_rubichess_trace(fen)
        
        # Get Stockfish evaluation
        print("[2/2] Running Stockfish evaluation...")
        stockfish_eval = self.run_stockfish_eval(fen)
        
        if not rubichess_trace or not stockfish_eval:
            print("[ERROR] Failed to get evaluations")
            return None
        
        # Calculate difference (convert Stockfish pawns to centipawns)
        stockfish_cp = stockfish_eval.final_eval * 100
        eval_difference = rubichess_trace.final_eval - stockfish_cp
        
        print(f"\n{'='*80}")
        print("EVALUATION COMPARISON")
        print(f"{'='*80}")
        print(f"RubiChess:  {rubichess_trace.final_eval:+6.0f} cp")
        print(f"Stockfish:  {stockfish_cp:+6.0f} cp")
        print(f"Difference: {eval_difference:+6.0f} cp (RubiChess {'over' if eval_difference > 0 else 'under'}evaluates)")
        
        print(f"\n{'='*80}")
        print("RUBICHESS COMPONENT BREAKDOWN")
        print(f"{'='*80}")
        print(f"{'Component':<15} {'MG':>8} {'EG':>8} {'Avg':>8}")
        print(f"{'-'*15} {'-'*8} {'-'*8} {'-'*8}")
        print(f"{'Material':<15} {rubichess_trace.material[0]:+8d} {rubichess_trace.material[1]:+8d} {(rubichess_trace.material[0]+rubichess_trace.material[1])/2:+8.1f}")
        print(f"{'Minors':<15} {rubichess_trace.minors[0]:+8d} {rubichess_trace.minors[1]:+8d} {(rubichess_trace.minors[0]+rubichess_trace.minors[1])/2:+8.1f}")
        print(f"{'Rooks':<15} {rubichess_trace.rooks[0]:+8d} {rubichess_trace.rooks[1]:+8d} {(rubichess_trace.rooks[0]+rubichess_trace.rooks[1])/2:+8.1f}")
        print(f"{'Pawns':<15} {rubichess_trace.pawns[0]:+8d} {rubichess_trace.pawns[1]:+8d} {(rubichess_trace.pawns[0]+rubichess_trace.pawns[1])/2:+8.1f}")
        print(f"{'Passers':<15} {rubichess_trace.passers[0]:+8d} {rubichess_trace.passers[1]:+8d} {(rubichess_trace.passers[0]+rubichess_trace.passers[1])/2:+8.1f}")
        print(f"{'Mobility':<15} {rubichess_trace.mobility[0]:+8d} {rubichess_trace.mobility[1]:+8d} {(rubichess_trace.mobility[0]+rubichess_trace.mobility[1])/2:+8.1f}")
        print(f"{'THREATS':<15} {rubichess_trace.threats[0]:+8d} {rubichess_trace.threats[1]:+8d} {(rubichess_trace.threats[0]+rubichess_trace.threats[1])/2:+8.1f}")
        print(f"{'King Attacks':<15} {rubichess_trace.king_attacks[0]:+8d} {rubichess_trace.king_attacks[1]:+8d} {(rubichess_trace.king_attacks[0]+rubichess_trace.king_attacks[1])/2:+8.1f}")
        
        # Analyze component discrepancies
        component_discrepancies = self._analyze_components(rubichess_trace, stockfish_eval)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(eval_difference, component_discrepancies)
        
        return ComparisonResult(
            fen=fen,
            position_id=position_id,
            rubichess=rubichess_trace,
            stockfish=stockfish_eval,
            eval_difference=eval_difference,
            component_discrepancies=component_discrepancies,
            recommendations=recommendations
        )
    
    def _analyze_components(self, rubichess: RubiChessTrace, stockfish: StockfishEval) -> Dict[str, float]:
        """Analyze discrepancies in evaluation components"""
        discrepancies = {}
        
        # Compare material/PSQT
        rubichess_material_cp = (rubichess.material[0] + rubichess.material[1]) / 2
        stockfish_material_cp = stockfish.material_psqt * 100
        discrepancies['material_psqt'] = rubichess_material_cp - stockfish_material_cp
        
        # Compare positional/mobility
        rubichess_positional_cp = (rubichess.mobility[0] + rubichess.mobility[1]) / 2
        stockfish_positional_cp = stockfish.positional * 100
        discrepancies['mobility_positional'] = rubichess_positional_cp - stockfish_positional_cp
        
        # Analyze individual RubiChess components
        discrepancies['minors'] = (rubichess.minors[0] + rubichess.minors[1]) / 2
        discrepancies['rooks'] = (rubichess.rooks[0] + rubichess.rooks[1]) / 2
        discrepancies['pawns'] = (rubichess.pawns[0] + rubichess.pawns[1]) / 2
        discrepancies['passers'] = (rubichess.passers[0] + rubichess.passers[1]) / 2
        discrepancies['threats'] = (rubichess.threats[0] + rubichess.threats[1]) / 2
        discrepancies['king_attacks'] = (rubichess.king_attacks[0] + rubichess.king_attacks[1]) / 2
        
        return discrepancies
    
    def _generate_recommendations(self, eval_diff: float, components: Dict[str, float]) -> List[str]:
        """Generate parameter tuning recommendations based on analysis"""
        recommendations = []
        
        # Overall evaluation discrepancy
        if abs(eval_diff) > 200:
            recommendations.append(f"CRITICAL DISCREPANCY: {abs(eval_diff):.0f}cp difference")
            recommendations.append("Priority: Immediate parameter review needed")
        elif abs(eval_diff) > 100:
            recommendations.append(f"SIGNIFICANT DISCREPANCY: {abs(eval_diff):.0f}cp difference")
            recommendations.append("Priority: Parameter tuning recommended")
        elif abs(eval_diff) > 50:
            recommendations.append(f"MODERATE DISCREPANCY: {abs(eval_diff):.0f}cp difference")
        
        # Analyze specific components (RubiChess-specific)
        if abs(components.get('threats', 0)) > 30:
            recommendations.append(f"THREATS: {components['threats']:+.1f}cp - Review threat evaluation parameters")
            recommendations.append("  -> Check eHangingpiecepenalty, threat bonuses")
        
        if abs(components.get('mobility_positional', 0)) > 50:
            recommendations.append(f"MOBILITY: {components['mobility_positional']:+.1f}cp difference vs Stockfish")
            recommendations.append("  -> Review eMobilitybonus array values")
        
        if abs(components.get('rooks', 0)) > 20:
            recommendations.append(f"ROOKS: {components['rooks']:+.1f}cp - Review rook evaluation")
            recommendations.append("  -> Check eRookon7thbonus, eRookonkingarea, eSlideronfreefilebonus")
        
        if abs(components.get('pawns', 0)) > 30:
            recommendations.append(f"PAWNS: {components['pawns']:+.1f}cp - Review pawn structure evaluation")
            recommendations.append("  -> Check pawn bonuses/penalties, passer evaluation")
        
        if abs(components.get('king_attacks', 0)) > 30:
            recommendations.append(f"KING SAFETY: {components['king_attacks']:+.1f}cp - Review king safety parameters")
            recommendations.append("  -> Check king attack weights, pawn shield bonuses")
        
        if abs(components.get('minors', 0)) > 20:
            recommendations.append(f"MINORS: {components['minors']:+.1f}cp - Review minor piece evaluation")
            recommendations.append("  -> Check bishop/knight positioning bonuses")
        
        # Direction indicator
        if eval_diff < -100:
            recommendations.append("TENDENCY: RubiChess undervalues this position type")
            recommendations.append("  -> Consider increasing relevant bonuses")
        elif eval_diff > 100:
            recommendations.append("TENDENCY: RubiChess overvalues this position type")
            recommendations.append("  -> Consider reducing relevant bonuses")
        
        return recommendations
    
    def analyze_all_positions(self) -> List[ComparisonResult]:
        """Analyze all target positions"""
        results = []
        
        for pos_id, fen in self.target_positions.items():
            result = self.compare_evaluations(pos_id, fen)
            if result:
                results.append(result)
            time.sleep(0.5)  # Brief pause between positions
        
        return results
    
    def generate_report(self, results: List[ComparisonResult], output_file: str = "phase2_component_analysis.md"):
        """Generate comprehensive analysis report"""
        with open(output_file, 'w') as f:
            f.write("# Phase 2: Evaluation Component Analysis Report\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Summary section
            f.write("## Executive Summary\n\n")
            avg_diff = sum(r.eval_difference for r in results) / len(results) if results else 0
            f.write(f"- **Positions Analyzed:** {len(results)}\n")
            f.write(f"- **Average Evaluation Difference:** {avg_diff:+.1f}cp\n")
            f.write(f"- **Largest Discrepancy:** {max((abs(r.eval_difference), r.position_id) for r in results)[1]} ")
            f.write(f"({max(abs(r.eval_difference) for r in results):.0f}cp)\n\n")
            
            # Detailed position analysis
            f.write("## Detailed Position Analysis\n\n")
            for result in results:
                f.write(f"### Position {result.position_id}\n\n")
                f.write(f"**FEN:** `{result.fen}`\n\n")
                
                f.write(f"#### Evaluation Summary\n\n")
                f.write(f"| Engine | Evaluation |\n")
                f.write(f"|--------|------------|\n")
                f.write(f"| RubiChess | {result.rubichess.final_eval:+d} cp |\n")
                f.write(f"| Stockfish | {result.stockfish.final_eval * 100:+.0f} cp |\n")
                f.write(f"| **Difference** | **{result.eval_difference:+.0f} cp** |\n\n")
                
                f.write(f"#### RubiChess Component Breakdown\n\n")
                f.write(f"| Component | Middlegame | Endgame | Average |\n")
                f.write(f"|-----------|------------|---------|----------|\n")
                f.write(f"| Material | {result.rubichess.material[0]:+d} | {result.rubichess.material[1]:+d} | {(result.rubichess.material[0]+result.rubichess.material[1])/2:+.1f} |\n")
                f.write(f"| Minors | {result.rubichess.minors[0]:+d} | {result.rubichess.minors[1]:+d} | {(result.rubichess.minors[0]+result.rubichess.minors[1])/2:+.1f} |\n")
                f.write(f"| Rooks | {result.rubichess.rooks[0]:+d} | {result.rubichess.rooks[1]:+d} | {(result.rubichess.rooks[0]+result.rubichess.rooks[1])/2:+.1f} |\n")
                f.write(f"| Pawns | {result.rubichess.pawns[0]:+d} | {result.rubichess.pawns[1]:+d} | {(result.rubichess.pawns[0]+result.rubichess.pawns[1])/2:+.1f} |\n")
                f.write(f"| Passers | {result.rubichess.passers[0]:+d} | {result.rubichess.passers[1]:+d} | {(result.rubichess.passers[0]+result.rubichess.passers[1])/2:+.1f} |\n")
                f.write(f"| Mobility | {result.rubichess.mobility[0]:+d} | {result.rubichess.mobility[1]:+d} | {(result.rubichess.mobility[0]+result.rubichess.mobility[1])/2:+.1f} |\n")
                f.write(f"| **Threats** | **{result.rubichess.threats[0]:+d}** | **{result.rubichess.threats[1]:+d}** | **{(result.rubichess.threats[0]+result.rubichess.threats[1])/2:+.1f}** |\n")
                f.write(f"| King Attacks | {result.rubichess.king_attacks[0]:+d} | {result.rubichess.king_attacks[1]:+d} | {(result.rubichess.king_attacks[0]+result.rubichess.king_attacks[1])/2:+.1f} |\n")
                f.write(f"| Complexity | {result.rubichess.complexity[0]:+d} | {result.rubichess.complexity[1]:+d} | {(result.rubichess.complexity[0]+result.rubichess.complexity[1])/2:+.1f} |\n")
                f.write(f"| Tempo | {result.rubichess.tempo[0]:+d} | {result.rubichess.tempo[1]:+d} | {(result.rubichess.tempo[0]+result.rubichess.tempo[1])/2:+.1f} |\n\n")
                
                f.write(f"#### Stockfish Component Breakdown\n\n")
                f.write(f"| Component | Value (pawns) | Value (cp) |\n")
                f.write(f"|-----------|---------------|------------|\n")
                f.write(f"| Material (PSQT) | {result.stockfish.material_psqt:+.2f} | {result.stockfish.material_psqt * 100:+.0f} |\n")
                f.write(f"| Positional (Layers) | {result.stockfish.positional:+.2f} | {result.stockfish.positional * 100:+.0f} |\n")
                f.write(f"| NNUE Eval | {result.stockfish.nnue_eval:+.2f} | {result.stockfish.nnue_eval * 100:+.0f} |\n")
                f.write(f"| Final Eval | {result.stockfish.final_eval:+.2f} | {result.stockfish.final_eval * 100:+.0f} |\n\n")
                
                f.write(f"#### Key Discrepancies\n\n")
                sorted_components = sorted(result.component_discrepancies.items(), 
                                         key=lambda x: abs(x[1]), reverse=True)
                for component, value in sorted_components:
                    if abs(value) > 10:  # Only show significant discrepancies
                        f.write(f"- **{component.replace('_', ' ').title()}**: {value:+.1f}cp\n")
                f.write("\n")
                
                f.write(f"#### Recommendations\n\n")
                for rec in result.recommendations:
                    f.write(f"{rec}\n")
                f.write("\n---\n\n")
            
            # Overall recommendations
            f.write("## Overall Recommendations\n\n")
            all_recs = set()
            for result in results:
                all_recs.update(result.recommendations)
            
            for i, rec in enumerate(sorted(all_recs), 1):
                f.write(f"{i}. {rec}\n")
            
            f.write("\n---\n\n")
            f.write("## Next Steps\n\n")
            f.write("1. Review component discrepancies\n")
            f.write("2. Implement parameter adjustments\n")
            f.write("3. Re-test positions for improvement\n")
            f.write("4. Validate no regressions on Phase 1 positions\n")
        
        print(f"\n[OK] Report generated: {output_file}")


def main():
    print("="*80)
    print("PHASE 2: EVALUATION COMPONENT COMPARISON TOOL")
    print("="*80)
    print("\nThis tool analyzes tactical positions to identify specific parameter")
    print("discrepancies between RubiChess and Stockfish evaluations.\n")
    
    comparator = EvaluationComparator()
    
    print("Target Positions:")
    for pos_id, fen in comparator.target_positions.items():
        print(f"  Position {pos_id}: {fen[:50]}...")
    
    print("\nStarting analysis...")
    
    # Run analysis
    results = comparator.analyze_all_positions()
    
    # Generate report
    if results:
        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"Analyzed {len(results)} positions")
        comparator.generate_report(results)
        print("\nCheck 'phase2_component_analysis.md' for detailed results")
    else:
        print("\n[ERROR] No results to report")


if __name__ == "__main__":
    main()
