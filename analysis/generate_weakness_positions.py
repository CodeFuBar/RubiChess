#!/usr/bin/env python3
"""
Generate 500+ chess positions specifically designed to expose engine weaknesses.
Focuses on positions known to be challenging for chess engines.
"""

import chess
import chess.pgn
import random
from typing import List, Tuple

def create_tactical_weakness_positions() -> List[chess.Board]:
    """Create positions with complex tactical motifs that engines often miss."""
    positions = []
    
    # Sacrifice patterns that require deep calculation
    tactical_fens = [
        # Greek gift sacrifices
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4",
        "r1bq1rk1/ppp2ppp/2n2n2/2bpp3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 w - - 0 6",
        
        # Complex queen sacrifices
        "r3k2r/ppp2ppp/2n1bn2/2bpp1q1/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 w kq - 0 8",
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5",
        
        # Deflection and decoy tactics
        "r2qkb1r/ppp2ppp/2n2n2/3pp3/2B1P1b1/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 6",
        "r1bqkb1r/pppp1p1p/2n2np1/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5",
        
        # Pin and skewer combinations
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 0 5",
        "r2qkb1r/ppp2ppp/2n2n2/3pp1b1/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 6",
        
        # Double attacks and forks
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4",
        "r2qkb1r/ppp2ppp/2n2n2/3pp1b1/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 6",
    ]
    
    for fen in tactical_fens:
        try:
            board = chess.Board(fen)
            if board.is_valid():
                positions.append(board.copy())
        except:
            continue
    
    return positions

def create_endgame_weakness_positions() -> List[chess.Board]:
    """Create complex endgame positions that expose evaluation weaknesses."""
    positions = []
    
    # Complex pawn endgames
    endgame_fens = [
        # Pawn breakthrough patterns
        "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
        "8/8/2k5/5p2/2K3p1/8/3P4/8 w - - 0 1",
        "8/8/1p1k4/3p4/3P4/1P1K4/8/8 w - - 0 1",
        
        # King and pawn vs king
        "8/8/8/4k3/4P3/4K3/8/8 w - - 0 1",
        "8/8/8/3k4/3P4/3K4/8/8 b - - 0 1",
        "8/8/8/2k5/2P5/2K5/8/8 w - - 0 1",
        
        # Rook endgames with pawns
        "8/8/8/8/8/3k4/3p4/3K3R w - - 0 1",
        "8/8/8/8/8/3K4/3P4/3k3r b - - 0 1",
        "r7/8/8/8/8/8/1P6/1K6 w - - 0 1",
        
        # Queen vs pawns
        "8/1p6/8/8/8/8/8/Q3k2K w - - 0 1",
        "8/2p5/8/8/8/8/8/q3K2k b - - 0 1",
        
        # Bishop vs knight endgames
        "8/8/8/3k4/3n4/3K4/3B4/8 w - - 0 1",
        "8/8/8/3K4/3N4/3k4/3b4/8 b - - 0 1",
    ]
    
    for fen in endgame_fens:
        try:
            board = chess.Board(fen)
            if board.is_valid():
                positions.append(board.copy())
        except:
            continue
    
    return positions

def create_positional_weakness_positions() -> List[chess.Board]:
    """Create positions with subtle positional elements."""
    positions = []
    
    positional_fens = [
        # Weak squares and outposts
        "r1bqkb1r/ppp2ppp/2n2n2/3pp3/3PP3/2N2N2/PPP2PPP/R1BQKB1R w KQkq - 0 5",
        "r1bq1rk1/ppp1bppp/2n2n2/3p4/3P4/2N1PN2/PPP1BPPP/R1BQ1RK1 w - - 0 7",
        
        # Pawn structure weaknesses
        "r1bqkb1r/pp3ppp/2n2n2/2ppp3/3PP3/2N2N2/PPP2PPP/R1BQKB1R w KQkq - 0 6",
        "r1bq1rk1/pp2bppp/2n2n2/2ppp3/3PP3/2N1BN2/PPP2PPP/R1BQ1RK1 w - - 0 8",
        
        # King safety issues
        "r1bq1rk1/ppp2ppp/2n2n2/2bpp3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQ - 0 6",
        "r1bqk2r/ppp2ppp/2n2n2/2bpp3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 0 6",
    ]
    
    for fen in positional_fens:
        try:
            board = chess.Board(fen)
            if board.is_valid():
                positions.append(board.copy())
        except:
            continue
    
    return positions

def generate_random_complex_positions(count: int) -> List[chess.Board]:
    """Generate random complex middlegame positions."""
    positions = []
    
    for _ in range(count):
        board = chess.Board()
        
        # Play 8-15 random moves to get to middlegame
        moves_played = 0
        target_moves = random.randint(8, 15)
        
        while moves_played < target_moves and not board.is_game_over():
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break
            
            # Prefer captures and checks to create complex positions
            captures = [m for m in legal_moves if board.is_capture(m)]
            checks = [m for m in legal_moves if board.gives_check(m)]
            
            if captures and random.random() < 0.4:
                move = random.choice(captures)
            elif checks and random.random() < 0.2:
                move = random.choice(checks)
            else:
                move = random.choice(legal_moves)
            
            board.push(move)
            moves_played += 1
        
        if not board.is_game_over() and len(list(board.legal_moves)) > 5:
            positions.append(board.copy())
        
        if len(positions) >= count:
            break
    
    return positions

def generate_weakness_test_suite() -> List[chess.Board]:
    """Generate comprehensive test suite targeting engine weaknesses."""
    print("Generating weakness-focused test positions...")
    
    all_positions = []
    
    # Tactical weakness positions (100 positions)
    print("Creating tactical weakness positions...")
    tactical_base = create_tactical_weakness_positions()
    
    # Expand tactical positions by playing 1-2 moves from each base position
    for base_pos in tactical_base:
        all_positions.append(base_pos.copy())
        
        # Generate variations
        for _ in range(9):  # 10 total per base position
            board = base_pos.copy()
            moves_to_play = random.randint(1, 3)
            
            for _ in range(moves_to_play):
                legal_moves = list(board.legal_moves)
                if not legal_moves or board.is_game_over():
                    break
                
                # Prefer tactical moves
                captures = [m for m in legal_moves if board.is_capture(m)]
                checks = [m for m in legal_moves if board.gives_check(m)]
                
                if captures and random.random() < 0.6:
                    move = random.choice(captures)
                elif checks and random.random() < 0.3:
                    move = random.choice(checks)
                else:
                    move = random.choice(legal_moves)
                
                board.push(move)
            
            if not board.is_game_over() and len(list(board.legal_moves)) > 3:
                all_positions.append(board.copy())
    
    # Endgame weakness positions (100 positions)
    print("Creating endgame weakness positions...")
    endgame_base = create_endgame_weakness_positions()
    
    for base_pos in endgame_base:
        all_positions.append(base_pos.copy())
        
        # Generate endgame variations
        for _ in range(7):  # 8 total per base position
            board = base_pos.copy()
            moves_to_play = random.randint(1, 2)
            
            for _ in range(moves_to_play):
                legal_moves = list(board.legal_moves)
                if not legal_moves or board.is_game_over():
                    break
                board.push(random.choice(legal_moves))
            
            if not board.is_game_over():
                all_positions.append(board.copy())
    
    # Positional weakness positions (100 positions)
    print("Creating positional weakness positions...")
    positional_base = create_positional_weakness_positions()
    
    for base_pos in positional_base:
        all_positions.append(base_pos.copy())
        
        # Generate positional variations
        for _ in range(15):  # 16 total per base position
            board = base_pos.copy()
            moves_to_play = random.randint(1, 4)
            
            for _ in range(moves_to_play):
                legal_moves = list(board.legal_moves)
                if not legal_moves or board.is_game_over():
                    break
                board.push(random.choice(legal_moves))
            
            if not board.is_game_over() and len(list(board.legal_moves)) > 4:
                all_positions.append(board.copy())
    
    # Random complex positions (200+ positions)
    print("Creating random complex positions...")
    random_positions = generate_random_complex_positions(250)
    all_positions.extend(random_positions)
    
    # Remove duplicates and invalid positions
    print("Validating and deduplicating positions...")
    unique_positions = []
    seen_fens = set()
    
    for pos in all_positions:
        try:
            if pos.is_valid() and not pos.is_game_over() and len(list(pos.legal_moves)) >= 3:
                fen = pos.fen()
                if fen not in seen_fens:
                    seen_fens.add(fen)
                    unique_positions.append(pos)
        except:
            continue
    
    print(f"Generated {len(unique_positions)} unique valid positions")
    return unique_positions[:520]  # Return up to 520 positions

def save_positions_to_pgn(positions: List[chess.Board], filename: str):
    """Save positions to PGN file."""
    print(f"Saving {len(positions)} positions to {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        for i, board in enumerate(positions, 1):
            game = chess.pgn.Game()
            game.setup(board)
            game.headers["Event"] = "Engine Weakness Test Suite"
            game.headers["Site"] = "Analysis"
            game.headers["Date"] = "2025.01.11"
            game.headers["Round"] = str(i)
            game.headers["White"] = "Test"
            game.headers["Black"] = "Position"
            game.headers["Result"] = "*"
            game.headers["FEN"] = board.fen()
            game.headers["SetUp"] = "1"
            
            print(game, file=f)
            print("", file=f)

def main():
    """Generate weakness-focused test suite."""
    print("=== Chess Engine Weakness Position Generator ===")
    
    # Generate positions
    positions = generate_weakness_test_suite()
    
    # Save to PGN
    save_positions_to_pgn(positions, 'weakness_test_positions.pgn')
    
    print(f"\n=== Generation Complete ===")
    print(f"Total positions generated: {len(positions)}")
    print(f"Saved to: weakness_test_positions.pgn")
    print(f"Ready for engine comparison testing!")

if __name__ == "__main__":
    main()
