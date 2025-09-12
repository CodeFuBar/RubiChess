#!/usr/bin/env python3
"""
Parse evaluation differences between RubiChess and Stockfish.
Since Stockfish crashed, we'll analyze RubiChess evaluations for patterns and outliers.
"""

import csv
import pandas as pd
import chess
import chess.pgn
from collections import defaultdict
import re

def classify_position_type(fen):
    """Classify position by material and structure"""
    board = chess.Board(fen)
    
    # Count material
    white_material = 0
    black_material = 0
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
                   chess.ROOK: 5, chess.QUEEN: 9}
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type != chess.KING:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                white_material += value
            else:
                black_material += value
    
    total_material = white_material + black_material
    
    # Classify by game phase
    if total_material <= 10:
        phase = "endgame"
    elif total_material <= 20:
        phase = "middlegame"
    else:
        phase = "opening"
    
    # Check for tactical patterns
    tactical_indicators = []
    
    # Check for checks
    if board.is_check():
        tactical_indicators.append("check")
    
    # Check for captures available
    captures = [move for move in board.legal_moves if board.is_capture(move)]
    if len(captures) > 3:
        tactical_indicators.append("many_captures")
    
    # Check for pawn structure issues
    white_pawns = len(board.pieces(chess.PAWN, chess.WHITE))
    black_pawns = len(board.pieces(chess.PAWN, chess.BLACK))
    
    if abs(white_pawns - black_pawns) >= 2:
        tactical_indicators.append("pawn_imbalance")
    
    # Check for piece activity
    white_pieces = len([p for p in board.piece_map().values() if p.color == chess.WHITE])
    black_pieces = len([p for p in board.piece_map().values() if p.color == chess.BLACK])
    
    if abs(white_pieces - black_pieces) >= 2:
        tactical_indicators.append("material_imbalance")
    
    return {
        "phase": phase,
        "total_material": total_material,
        "material_balance": white_material - black_material,
        "tactical_indicators": tactical_indicators
    }

def analyze_evaluation_patterns(csv_file):
    """Analyze evaluation differences between RubiChess and Stockfish"""
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found. Please run engine comparison first.")
        return
    
    # Separate engine data
    rubichess_data = df[df['engine'] == 'RubiChess'].copy()
    stockfish_data = df[df['engine'] == 'Stockfish'].copy()
    
    if rubichess_data.empty:
        print("No RubiChess data found in CSV file.")
        return
    
    if stockfish_data.empty:
        print("No Stockfish data found in CSV file.")
        return
    
    print(f"Analyzing {len(rubichess_data)} RubiChess vs {len(stockfish_data)} Stockfish evaluations...")
    
    # Create comparison pairs
    comparison_data = []
    for _, rubi_row in rubichess_data.iterrows():
        stock_row = stockfish_data[stockfish_data['position_id'] == rubi_row['position_id']]
        if not stock_row.empty:
            stock_row = stock_row.iloc[0]
            
            pos_type = classify_position_type(rubi_row['fen'])
            eval_diff = rubi_row['evaluation_cp'] - stock_row['evaluation_cp']
            
            comparison_data.append({
                'position_id': rubi_row['position_id'],
                'fen': rubi_row['fen'],
                'rubichess_eval': rubi_row['evaluation_cp'],
                'stockfish_eval': stock_row['evaluation_cp'],
                'eval_difference': eval_diff,
                'abs_eval_difference': abs(eval_diff),
                'rubichess_move': rubi_row['best_move'],
                'stockfish_move': stock_row['best_move'],
                'move_agreement': rubi_row['best_move'] == stock_row['best_move'],
                'phase': pos_type['phase'],
                'total_material': pos_type['total_material'],
                'material_balance': pos_type['material_balance'],
                'tactical_indicators': ','.join(pos_type['tactical_indicators'])
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    print(f"\n=== Engine Comparison Analysis ===")
    print(f"Positions compared: {len(comparison_df)}")
    print(f"Move agreement: {comparison_df['move_agreement'].sum()}/{len(comparison_df)} ({comparison_df['move_agreement'].mean()*100:.1f}%)")
    print(f"Mean evaluation difference: {comparison_df['eval_difference'].mean():.1f} cp")
    print(f"Mean absolute difference: {comparison_df['abs_eval_difference'].mean():.1f} cp")
    print(f"Max absolute difference: {comparison_df['abs_eval_difference'].max():.1f} cp")
    
    # Find positions with large evaluation differences
    large_diff_threshold = 100  # cp
    large_differences = comparison_df[comparison_df['abs_eval_difference'] > large_diff_threshold]
    
    print(f"\n=== Large Evaluation Differences (>{large_diff_threshold}cp) ===")
    print(f"Found {len(large_differences)} positions with large evaluation differences:")
    
    flagged_positions = []
    
    for _, row in large_differences.iterrows():
        flagged_positions.append({
            'position_id': row['position_id'],
            'fen': row['fen'],
            'rubichess_eval': row['rubichess_eval'],
            'stockfish_eval': row['stockfish_eval'],
            'eval_difference': row['eval_difference'],
            'rubichess_move': row['rubichess_move'],
            'stockfish_move': row['stockfish_move'],
            'move_agreement': row['move_agreement'],
            'phase': row['phase'],
            'reason': f"Large evaluation difference: {row['eval_difference']:+.0f}cp"
        })
        
        agreement_str = "AGREE" if row['move_agreement'] else "DIFFER"
        print(f"Position {row['position_id']}: RubiChess {row['rubichess_eval']:+}cp vs Stockfish {row['stockfish_eval']:+}cp (diff: {row['eval_difference']:+}cp) [{agreement_str}]")
        print(f"  Moves: RubiChess {row['rubichess_move']} vs Stockfish {row['stockfish_move']} ({row['phase']})")
    
    # Analyze by game phase
    print(f"\n=== Evaluation Differences by Game Phase ===")
    phase_stats = comparison_df.groupby('phase')['abs_eval_difference'].agg(['count', 'mean', 'std', 'max'])
    print(phase_stats)
    
    # Move agreement by phase
    print(f"\n=== Move Agreement by Game Phase ===")
    move_agreement_stats = comparison_df.groupby('phase')['move_agreement'].agg(['count', 'sum', 'mean'])
    move_agreement_stats['agreement_pct'] = move_agreement_stats['mean'] * 100
    print(move_agreement_stats)
    
    # Look for systematic biases
    print(f"\n=== Systematic Analysis ===")
    rubi_higher = comparison_df[comparison_df['eval_difference'] > 50]
    stock_higher = comparison_df[comparison_df['eval_difference'] < -50]
    
    print(f"Positions where RubiChess evaluates >50cp higher: {len(rubi_higher)}")
    print(f"Positions where Stockfish evaluates >50cp higher: {len(stock_higher)}")
    
    if len(rubi_higher) > 0:
        print(f"RubiChess optimistic bias in phases: {rubi_higher['phase'].value_counts().to_dict()}")
    
    if len(stock_higher) > 0:
        print(f"Stockfish optimistic bias in phases: {stock_higher['phase'].value_counts().to_dict()}")
    
    # Save flagged positions
    flagged_df = pd.DataFrame(flagged_positions)
    flagged_df.to_csv('evaluation_differences.csv', index=False)
    
    # Create markdown summary
    create_evaluation_summary(comparison_df, flagged_positions, phase_stats)
    
    print(f"\nAnalysis complete!")
    print(f"Flagged {len(flagged_positions)} positions for review")
    print(f"Results saved to evaluation_differences.csv and evaluation_summary.md")

def create_evaluation_summary(comparison_data, flagged_positions, phase_stats):
    """Create markdown summary of evaluation analysis"""
    
    with open('evaluation_summary.md', 'w') as f:
        f.write("# RubiChess vs Stockfish Evaluation Analysis Summary\n\n")
        
        f.write("## Overview\n")
        f.write(f"- Total positions compared: {len(comparison_data)}\n")
        f.write(f"- Flagged positions: {len(flagged_positions)}\n")
        f.write(f"- Move agreement: {comparison_data['move_agreement'].mean()*100:.1f}%\n")
        f.write(f"- Mean absolute difference: {comparison_data['abs_eval_difference'].mean():.1f} cp\n")
        f.write(f"- Max absolute difference: {comparison_data['abs_eval_difference'].max():.1f} cp\n\n")
        
        f.write("## Evaluation by Game Phase\n")
        f.write("| Phase | Count | Mean (cp) | Std Dev (cp) |\n")
        f.write("|-------|-------|-----------|-------------|\n")
        for phase, stats in phase_stats.iterrows():
            f.write(f"| {phase} | {stats['count']} | {stats['mean']:.1f} | {stats['std']:.1f} |\n")
        f.write("\n")
        
        f.write("## Flagged Positions\n")
        f.write("Positions with large evaluation differences (>100cp):\n\n")
        
        for i, pos in enumerate(flagged_positions, 1):
            f.write(f"### Position {i} (ID: {pos['position_id']})\n")
            f.write(f"- **FEN**: `{pos['fen']}`\n")
            f.write(f"- **RubiChess**: {pos['rubichess_eval']} cp ({pos['rubichess_move']})\n")
            f.write(f"- **Stockfish**: {pos['stockfish_eval']} cp ({pos['stockfish_move']})\n")
            f.write(f"- **Difference**: {pos['eval_difference']:+} cp\n")
            f.write(f"- **Move Agreement**: {'Yes' if pos['move_agreement'] else 'No'}\n")
            f.write(f"- **Game Phase**: {pos['phase']}\n")
            f.write(f"- **Reason**: {pos['reason']}\n\n")
        
        f.write("## Recommendations\n")
        f.write("Based on this comparison analysis, consider investigating:\n\n")
        f.write("1. **Large Evaluation Differences**: Focus on positions where engines disagree by >100cp\n")
        f.write("2. **Move Disagreements**: Positions where engines choose different moves may reveal tactical blind spots\n")
        f.write("3. **Systematic Biases**: Check if RubiChess consistently over/under-evaluates certain position types\n")
        f.write("4. **Phase-Specific Issues**: Analyze performance differences across opening/middlegame/endgame\n\n")
        
        f.write("## Next Steps\n")
        f.write("1. Manual review of flagged positions\n")
        f.write("2. Compare with other engines (when Stockfish issues are resolved)\n")
        f.write("3. Profile RubiChess evaluation function performance\n")
        f.write("4. Focus optimization efforts on identified weak areas\n")

def main():
    """Main analysis function"""
    print("Parsing large-scale engine comparison data...")
    analyze_evaluation_patterns('large_scale_engine_comparison.csv')

if __name__ == "__main__":
    main()
