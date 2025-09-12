#!/usr/bin/env python3
"""
Generate diverse chess test positions for engine evaluation comparison.
Covers tactical, positional, and endgame motifs.
"""

import chess
import chess.pgn
import random
from io import StringIO

def create_tactical_positions():
    """Generate positions with tactical motifs (forks, pins, skewers, etc.)"""
    positions = []
    
    # Fork positions
    positions.extend([
        "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4",  # Knight fork setup
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5",  # Bishop fork threat
        "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5",  # Double fork setup
    ])
    
    # Pin positions
    positions.extend([
        "rnbqkbnr/ppp2ppp/3p4/4p3/4P3/3P1N2/PPP2PPP/RNBQKB1R b KQkq - 0 4",  # Pin on f-file
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 5",  # Pin on diagonal
        "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 5",  # Mutual pins
    ])
    
    # Skewer positions
    positions.extend([
        "r3k2r/ppp2ppp/2n1bn2/2bpp3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 8",  # Skewer setup
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 6",  # Back rank skewer
    ])
    
    # Discovered attacks
    positions.extend([
        "rnbqkb1r/ppp2ppp/3p1n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 5",  # Discovered check setup
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5",  # Discovered attack
    ])
    
    return positions

def create_positional_positions():
    """Generate positions with positional motifs"""
    positions = []
    
    # Pawn structure positions
    positions.extend([
        "rnbqkb1r/pp3ppp/3ppn2/8/3PP3/2N2N2/PPP2PPP/R1BQKB1R w KQkq - 0 6",  # Pawn center
        "rnbqkb1r/ppp2ppp/3p1n2/4p3/4P3/3P1N2/PPP2PPP/RNBQKB1R b KQkq - 0 5",  # Isolated pawn
        "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/3P1N2/PPP2PPP/RNBQKB1R w KQkq c6 0 5",  # Doubled pawns
        "rnbqkb1r/ppp1pppp/3p1n2/8/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq d3 0 4",  # Backward pawn
    ])
    
    # Open files and weak squares
    positions.extend([
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/3P1N2/PPP2PPP/RNBQKB1R w KQkq - 0 5",  # Semi-open file
        "rnbqk2r/pppp1ppp/4pn2/8/1b2P3/3P1N2/PPP2PPP/RNBQKB1R w KQkq - 0 5",  # Weak squares
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2NP1N2/PPP2PPP/R1BQKB1R b KQkq - 0 5",  # Outpost squares
    ])
    
    # King safety positions
    positions.extend([
        "rnbqk2r/pppp1ppp/4pn2/8/1b2P3/3P1N2/PPP2PPP/RNBQKB1R b KQkq - 0 5",  # Uncastled king
        "rnbq1rk1/pppp1ppp/4pn2/8/1b2P3/3P1N2/PPP2PPP/RNBQKB1R w KQ - 0 6",  # Castled vs uncastled
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 6",  # Opposite castling
    ])
    
    return positions

def create_endgame_positions():
    """Generate endgame positions"""
    positions = []
    
    # King and pawn endings
    positions.extend([
        "8/8/8/3k4/3P4/3K4/8/8 w - - 0 1",  # Basic K+P vs K
        "8/8/8/2k5/2P5/2K5/8/8 b - - 0 1",  # Opposition
        "8/8/3k4/8/3P4/3K4/8/8 w - - 0 1",  # Pawn breakthrough
        "8/2k5/8/2P5/8/2K5/8/8 w - - 0 1",  # Advanced pawn
        "8/8/8/3k1p2/3P1P2/3K4/8/8 w - - 0 1",  # Pawn race
    ])
    
    # Minor piece endings
    positions.extend([
        "8/8/8/3k4/8/3K1N2/8/8 w - - 0 1",  # K+N vs K (draw)
        "8/8/8/3k4/8/3KB3/8/8 w - - 0 1",  # K+B vs K (draw)
        "8/8/8/3k4/3p4/3KB3/8/8 w - - 0 1",  # K+B vs K+P
        "8/8/8/3k1n2/8/3K1N2/8/8 w - - 0 1",  # K+N vs K+N
        "8/8/8/3k1b2/8/3K1B2/8/8 w - - 0 1",  # K+B vs K+B same color
        "8/8/8/2k2b2/8/3K1B2/8/8 w - - 0 1",  # K+B vs K+B opposite color
    ])
    
    # Rook endings
    positions.extend([
        "8/8/8/3k4/8/3K1R2/8/8 w - - 0 1",  # K+R vs K
        "8/8/8/3k4/3r4/3K1R2/8/8 w - - 0 1",  # K+R vs K+R
        "8/8/8/3k4/3rp3/3K1R2/8/8 w - - 0 1",  # K+R vs K+R+P
        "8/8/8/3k4/3r4/3KR3/8/8 w - - 0 1",  # Lucena position setup
        "8/8/8/8/8/3k1r2/3R4/3K4 b - - 0 1",  # Philidor position
    ])
    
    # Queen endings
    positions.extend([
        "8/8/8/3k4/8/3K1Q2/8/8 w - - 0 1",  # K+Q vs K
        "8/8/8/3k4/3q4/3K1Q2/8/8 w - - 0 1",  # K+Q vs K+Q
        "8/8/8/3k4/3qp3/3K1Q2/8/8 w - - 0 1",  # K+Q vs K+Q+P
    ])
    
    return positions

def create_complex_middlegame_positions():
    """Generate complex middlegame positions from famous games"""
    positions = []
    
    # Famous tactical positions
    positions.extend([
        "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 0 4",  # Italian Game
        "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq c6 0 4",  # Caro-Kann
        "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/6P1/PP2PP1P/RNBQKBNR b KQkq c3 0 4",  # English Opening
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5",  # Italian Game variation
        "rnbqk1nr/pppp1ppp/4p3/8/1b2P3/3P1N2/PPP2PPP/RNBQKB1R b KQkq - 0 4",  # Nimzo-Indian setup
    ])
    
    # Strategic positions
    positions.extend([
        "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 w - - 0 8",  # Closed center
        "r1bqk2r/pp2nppp/2np4/2p1p3/2P1P3/2NP1N2/PP3PPP/R1BQKB1R w KQkq - 0 8",  # Pawn chains
        "r2q1rk1/ppp2ppp/2n1bn2/2bpp3/3PP3/2N2N2/PPP1BPPP/R1BQ1RK1 w - - 0 9",  # Piece coordination
    ])
    
    return positions

def generate_random_positions(count=50):
    """Generate random legal positions"""
    positions = []
    
    for _ in range(count):
        board = chess.Board()
        # Make random moves to create diverse positions
        moves_count = random.randint(10, 40)
        
        for _ in range(moves_count):
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            board.push(move)
            
            # Stop if game is over
            if board.is_game_over():
                break
        
        if not board.is_game_over():
            positions.append(board.fen())
    
    return positions

def main():
    """Generate all test positions and save to PGN file"""
    print("Generating diverse chess test positions...")
    
    all_positions = []
    
    # Generate different types of positions
    tactical_positions = create_tactical_positions()
    positional_positions = create_positional_positions()
    endgame_positions = create_endgame_positions()
    complex_positions = create_complex_middlegame_positions()
    random_positions = generate_random_positions(50)
    
    all_positions.extend(tactical_positions)
    all_positions.extend(positional_positions)
    all_positions.extend(endgame_positions)
    all_positions.extend(complex_positions)
    all_positions.extend(random_positions)
    
    print(f"Generated {len(all_positions)} positions:")
    print(f"  - Tactical: {len(tactical_positions)}")
    print(f"  - Positional: {len(positional_positions)}")
    print(f"  - Endgame: {len(endgame_positions)}")
    print(f"  - Complex middlegame: {len(complex_positions)}")
    print(f"  - Random: {len(random_positions)}")
    
    # Create PGN file
    pgn_content = StringIO()
    
    for i, fen in enumerate(all_positions, 1):
        try:
            board = chess.Board(fen)
            game = chess.pgn.Game()
            game.headers["Event"] = "Engine Test Suite"
            game.headers["Site"] = "Computer"
            game.headers["Date"] = "2025.09.10"
            game.headers["Round"] = str(i)
            game.headers["White"] = "Test"
            game.headers["Black"] = "Test"
            game.headers["Result"] = "*"
            game.headers["FEN"] = fen
            game.headers["SetUp"] = "1"
            
            # Set up the position
            game.setup(board)
            
            print(game, file=pgn_content)
            print("", file=pgn_content)  # Empty line between games
            
        except Exception as e:
            print(f"Error with position {i}: {fen} - {e}")
            continue
    
    # Write to file
    with open("positions.pgn", "w") as f:
        f.write(pgn_content.getvalue())
    
    print(f"\nSaved {len(all_positions)} positions to positions.pgn")
    print("Ready for engine comparison testing!")

if __name__ == "__main__":
    main()
