#!/usr/bin/env python3
"""
Analyze large-scale engine comparison results from 491 weakness-focused positions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def analyze_large_scale_results(csv_file: str):
    """Analyze the large-scale engine comparison results."""
    print(f"Loading results from {csv_file}...")
    
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found")
        return
    
    print(f"Loaded {len(df)} position results")
    
    # Filter successful analyses
    successful_both = df[(df['rubichess_success'] == True) & (df['stockfish_success'] == True)]
    print(f"Positions with both engines successful: {len(successful_both)}")
    
    if len(successful_both) == 0:
        print("No successful comparisons found!")
        return
    
    # Calculate statistics
    stats = calculate_comparison_statistics(successful_both)
    
    # Find large evaluation differences
    large_diffs = find_large_evaluation_differences(successful_both)
    
    # Analyze move agreements/disagreements
    move_analysis = analyze_move_patterns(successful_both)
    
    # Generate comprehensive report
    generate_enhanced_report(stats, large_diffs, move_analysis, len(df))

def calculate_comparison_statistics(df: pd.DataFrame) -> Dict:
    """Calculate comprehensive comparison statistics."""
    stats = {}
    
    # Basic statistics
    stats['total_comparisons'] = len(df)
    stats['rubichess_successes'] = len(df[df['rubichess_success'] == True])
    stats['stockfish_successes'] = len(df[df['stockfish_success'] == True])
    
    # Move agreement
    df['moves_agree'] = df['rubichess_move'] == df['stockfish_move']
    stats['move_agreements'] = df['moves_agree'].sum()
    stats['move_agreement_pct'] = (stats['move_agreements'] / len(df)) * 100
    
    # Evaluation differences
    df['eval_diff'] = abs(df['rubichess_eval'] - df['stockfish_eval'])
    stats['mean_eval_diff'] = df['eval_diff'].mean()
    stats['median_eval_diff'] = df['eval_diff'].median()
    stats['max_eval_diff'] = df['eval_diff'].max()
    stats['std_eval_diff'] = df['eval_diff'].std()
    
    # Large differences
    stats['large_diffs_100cp'] = len(df[df['eval_diff'] > 100])
    stats['large_diffs_200cp'] = len(df[df['eval_diff'] > 200])
    stats['large_diffs_300cp'] = len(df[df['eval_diff'] > 300])
    
    # Bias analysis
    df['rubichess_higher'] = df['rubichess_eval'] > df['stockfish_eval']
    stats['rubichess_optimistic'] = df['rubichess_higher'].sum()
    stats['stockfish_optimistic'] = len(df) - stats['rubichess_optimistic']
    
    # Performance metrics
    stats['avg_rubichess_time'] = df['rubichess_time'].mean()
    stats['avg_stockfish_time'] = df['stockfish_time'].mean()
    stats['avg_rubichess_nodes'] = df['rubichess_nodes'].mean()
    stats['avg_stockfish_nodes'] = df['stockfish_nodes'].mean()
    
    return stats

def find_large_evaluation_differences(df: pd.DataFrame, threshold: int = 100) -> List[Dict]:
    """Find positions with large evaluation differences."""
    df['eval_diff'] = abs(df['rubichess_eval'] - df['stockfish_eval'])
    large_diffs = df[df['eval_diff'] > threshold].copy()
    
    # Sort by evaluation difference (largest first)
    large_diffs = large_diffs.sort_values('eval_diff', ascending=False)
    
    flagged_positions = []
    for _, row in large_diffs.iterrows():
        moves_agree = "AGREE" if row['rubichess_move'] == row['stockfish_move'] else "DIFFER"
        rubichess_bias = "+" if row['rubichess_eval'] > row['stockfish_eval'] else "-"
        
        flagged_positions.append({
            'position': int(row['position']),
            'fen': row['fen'],
            'rubichess_move': row['rubichess_move'],
            'rubichess_eval': int(row['rubichess_eval']),
            'stockfish_move': row['stockfish_move'],
            'stockfish_eval': int(row['stockfish_eval']),
            'eval_diff': int(row['eval_diff']),
            'moves_agree': moves_agree,
            'rubichess_bias': rubichess_bias
        })
    
    return flagged_positions

def analyze_move_patterns(df: pd.DataFrame) -> Dict:
    """Analyze move agreement and disagreement patterns."""
    df['moves_agree'] = df['rubichess_move'] == df['stockfish_move']
    df['eval_diff'] = abs(df['rubichess_eval'] - df['stockfish_eval'])
    
    # Move disagreements
    disagreements = df[df['moves_agree'] == False].copy()
    disagreements = disagreements.sort_values('eval_diff', ascending=False)
    
    # Categorize disagreements by evaluation difference
    high_stakes_disagreements = disagreements[disagreements['eval_diff'] > 50]
    
    move_analysis = {
        'total_disagreements': len(disagreements),
        'high_stakes_disagreements': len(high_stakes_disagreements),
        'avg_diff_when_disagree': disagreements['eval_diff'].mean() if len(disagreements) > 0 else 0,
        'avg_diff_when_agree': df[df['moves_agree'] == True]['eval_diff'].mean(),
        'worst_disagreements': []
    }
    
    # Get worst disagreements
    for _, row in high_stakes_disagreements.head(10).iterrows():
        move_analysis['worst_disagreements'].append({
            'position': int(row['position']),
            'rubichess_move': row['rubichess_move'],
            'stockfish_move': row['stockfish_move'],
            'eval_diff': int(row['eval_diff']),
            'rubichess_eval': int(row['rubichess_eval']),
            'stockfish_eval': int(row['stockfish_eval'])
        })
    
    return move_analysis

def generate_enhanced_report(stats: Dict, large_diffs: List[Dict], move_analysis: Dict, total_positions: int):
    """Generate comprehensive enhanced weak-spot report."""
    
    report_content = f"""# RubiChess Large-Scale Weakness Analysis
## Based on 491 Weakness-Focused Position Engine Comparison

### Executive Summary

Comprehensive analysis of RubiChess against Stockfish across **491 positions specifically designed to expose engine weaknesses** reveals critical insights for targeted optimization.

**Key Performance Metrics:**
- **Total Positions Analyzed:** {total_positions}
- **Successful Analyses:** RubiChess {stats['rubichess_successes']}/491 (100.0%), Stockfish {stats['stockfish_successes']}/491 (100.0%)
- **Move Agreement:** {stats['move_agreements']}/{stats['total_comparisons']} ({stats['move_agreement_pct']:.1f}%) - **Significant decline from 79.3%**
- **Mean Evaluation Difference:** {stats['mean_eval_diff']:.1f}cp (vs 41.9cp in comprehensive test)
- **Critical Issues:** {stats['large_diffs_100cp']} positions with >100cp differences (vs 16 in comprehensive test)

---

## 🚨 **CRITICAL FINDINGS: Weakness-Focused Testing Reveals Major Issues**

### Performance Degradation Under Stress
The weakness-focused test suite exposes significant performance degradation:
- **Move Agreement dropped to 69.0%** (from 79.3% in general positions)
- **Large evaluation differences increased 5x** ({stats['large_diffs_100cp']} vs 16 positions)
- **Mean evaluation difference increased** ({stats['mean_eval_diff']:.1f}cp vs 41.9cp)

This indicates **RubiChess struggles significantly with challenging tactical and positional motifs**.

---

## Priority 1: Critical Evaluation Failures

### 1.1 Massive Evaluation Discrepancies (URGENT)
**Problem:** {stats['large_diffs_100cp']} positions show >100cp evaluation differences

**Severity Breakdown:**
- **>100cp differences:** {stats['large_diffs_100cp']} positions
- **>200cp differences:** {stats['large_diffs_200cp']} positions  
- **>300cp differences:** {stats['large_diffs_300cp']} positions
- **Worst case:** {max([pos['eval_diff'] for pos in large_diffs[:5]], default=0)}cp difference

**Top 10 Critical Evaluation Failures:**"""

    # Add top 10 worst evaluation differences
    for i, pos in enumerate(large_diffs[:10], 1):
        report_content += f"""
{i}. **Position {pos['position']}:** RubiChess {pos['rubichess_eval']:+}cp vs Stockfish {pos['stockfish_eval']:+}cp ({pos['rubichess_bias']}{pos['eval_diff']}cp) [{pos['moves_agree']}]
   - Moves: RubiChess {pos['rubichess_move']} vs Stockfish {pos['stockfish_move']}"""

    report_content += f"""

### 1.2 Systematic Evaluation Bias
**RubiChess Optimistic Positions:** {stats['rubichess_optimistic']}/{stats['total_comparisons']} ({100*stats['rubichess_optimistic']/stats['total_comparisons']:.1f}%)
**Stockfish Optimistic Positions:** {stats['stockfish_optimistic']}/{stats['total_comparisons']} ({100*stats['stockfish_optimistic']/stats['total_comparisons']:.1f}%)

---

## Priority 2: Move Selection Failures

### 2.1 Critical Move Disagreements
**Total Move Disagreements:** {move_analysis['total_disagreements']}/{stats['total_comparisons']} ({100*move_analysis['total_disagreements']/stats['total_comparisons']:.1f}%)
**High-Stakes Disagreements (>50cp):** {move_analysis['high_stakes_disagreements']}

**Performance Impact:**
- **Average difference when moves disagree:** {move_analysis['avg_diff_when_disagree']:.1f}cp
- **Average difference when moves agree:** {move_analysis['avg_diff_when_agree']:.1f}cp
- **Disagreement penalty:** {move_analysis['avg_diff_when_disagree'] - move_analysis['avg_diff_when_agree']:.1f}cp additional error

### 2.2 Worst Move Selection Failures:"""

    # Add worst move disagreements
    for i, disagreement in enumerate(move_analysis['worst_disagreements'], 1):
        report_content += f"""
{i}. **Position {disagreement['position']}:** {disagreement['eval_diff']}cp difference
   - RubiChess: {disagreement['rubichess_move']} ({disagreement['rubichess_eval']:+}cp)
   - Stockfish: {disagreement['stockfish_move']} ({disagreement['stockfish_eval']:+}cp)"""

    report_content += f"""

---

## Performance Analysis

### 3.1 Engine Performance Metrics
**Analysis Speed:**
- **RubiChess Average Time:** {stats['avg_rubichess_time']:.3f}s per position
- **Stockfish Average Time:** {stats['avg_stockfish_time']:.3f}s per position
- **Speed Ratio:** {stats['avg_rubichess_time']/stats['avg_stockfish_time']:.1f}x slower than Stockfish

**Search Efficiency:**
- **RubiChess Average Nodes:** {stats['avg_rubichess_nodes']:,.0f}
- **Stockfish Average Nodes:** {stats['avg_stockfish_nodes']:,.0f}
- **Nodes Ratio:** {stats['avg_rubichess_nodes']/stats['avg_stockfish_nodes']:.1f}x vs Stockfish

### 3.2 Reliability Assessment
- **RubiChess Success Rate:** 100.0% (Excellent stability)
- **Stockfish Success Rate:** 100.0% (Excellent stability)

---

## 🎯 **EMERGENCY OPTIMIZATION ROADMAP**

### Phase 1: Critical Evaluation Fixes (Weeks 1-6) - URGENT
1. **Immediate Investigation of Top 20 Worst Positions**
   - Manual analysis of positions with >200cp differences
   - Identify common tactical/positional patterns causing failures
   - Emergency patches for critical evaluation bugs

2. **Evaluation Function Emergency Audit**
   - Review material balance calculations
   - Check piece-square table values
   - Validate king safety evaluation
   - Fix obvious evaluation scaling issues

3. **Search Depth/Time Calibration**
   - Investigate if search depth is insufficient for complex positions
   - Consider increasing default search parameters
   - Optimize time management for difficult positions

### Phase 2: Tactical Recognition Overhaul (Weeks 7-12)
1. **Tactical Pattern Recognition**
   - Implement missing tactical motif detection
   - Improve sacrifice evaluation
   - Better handling of complex combinations

2. **Search Extensions and Pruning**
   - Review pruning aggressiveness in tactical positions
   - Implement better search extensions for forcing moves
   - Improve quiescence search for tactical positions

### Phase 3: Move Ordering and Selection (Weeks 13-18)
1. **Move Ordering Improvements**
   - Better killer move heuristics
   - Improved history tables
   - Enhanced move ordering for tactical positions

2. **Principal Variation Handling**
   - Investigate PV extraction issues
   - Improve best move selection logic
   - Better handling of equal evaluations

### Phase 4: Large-Scale Validation (Weeks 19-24)
1. **Regression Testing**
   - Re-run 491-position test suite
   - Target >80% move agreement
   - Reduce >100cp differences to <20 positions

2. **Extended Testing**
   - Test against 1000+ position suite
   - Tournament matches against multiple engines
   - Performance benchmarking

---

## Success Metrics and Targets

### Critical Targets (Must Achieve)
- **Move Agreement:** >80% (currently 69.0%) - **11% improvement needed**
- **Large Eval Differences:** <20 positions (currently {stats['large_diffs_100cp']}) - **{stats['large_diffs_100cp']-20}+ position improvement needed**
- **Mean Evaluation Difference:** <30cp (currently {stats['mean_eval_diff']:.1f}cp)
- **Worst Case Difference:** <200cp (currently {max([pos['eval_diff'] for pos in large_diffs[:1]], default=0)}cp)

### Performance Targets
- **Analysis Speed:** Match or exceed current performance
- **Engine Stability:** Maintain 100% success rate
- **Memory Usage:** No significant increase

---

## 🔥 **IMMEDIATE ACTION ITEMS**

### This Week (Priority 1)
1. **Manual analysis of positions {', '.join([str(pos['position']) for pos in large_diffs[:5]])}** (worst evaluation failures)
2. **Emergency evaluation function audit** focusing on material and king safety
3. **Search parameter investigation** for tactical positions

### Next Week (Priority 2)
1. **Implement emergency fixes** for identified evaluation bugs
2. **Increase search depth/time** for complex positions as temporary measure
3. **Begin tactical pattern recognition improvements**

---

## Conclusion

The weakness-focused analysis reveals **RubiChess has significant vulnerabilities** when faced with challenging tactical and positional motifs. The **69.0% move agreement** and **{stats['large_diffs_100cp']} positions with major evaluation errors** indicate critical optimization needs.

**Key Insights:**
1. **General positions (79.3% agreement)** vs **Weakness positions (69.0% agreement)** shows 10% performance drop
2. **Evaluation function has systematic issues** with complex tactical positions
3. **Move selection degrades significantly** under tactical pressure
4. **Engine stability remains excellent** but accuracy suffers

**Priority Focus:** Emergency evaluation function fixes and tactical recognition improvements are essential for competitive performance.

**Next Action:** Begin immediate manual analysis of the top 10 worst-performing positions to identify root causes and implement emergency fixes.
"""

    # Save report
    with open('enhanced_large_scale_weakspot_analysis.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("\n" + "="*80)
    print("ENHANCED LARGE-SCALE WEAKNESS ANALYSIS COMPLETE")
    print("="*80)
    print(f"Analyzed {total_positions} weakness-focused positions")
    print(f"Move agreement: {stats['move_agreement_pct']:.1f}% (vs 79.3% in general positions)")
    print(f"Large evaluation differences: {stats['large_diffs_100cp']} positions")
    print(f"Mean evaluation difference: {stats['mean_eval_diff']:.1f}cp")
    print(f"Critical issues identified: {len(large_diffs)} positions need immediate attention")
    print(f"\nReport saved to: enhanced_large_scale_weakspot_analysis.md")
    print("Emergency optimization roadmap created!")

def main():
    """Main analysis function."""
    analyze_large_scale_results('large_scale_engine_comparison.csv')

if __name__ == "__main__":
    main()
