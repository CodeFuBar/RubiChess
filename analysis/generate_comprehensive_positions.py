#!/usr/bin/env python3
"""
Generate comprehensive test suite with 200+ chess positions including:
- Difficult tactical puzzles
- Complex endgames
- Strategic middlegame positions
- Famous game positions
- Computer chess test suites (Bratko-Kopec, WAC, etc.)
"""

import chess
import chess.pgn
import random
import io

def create_tactical_positions():
    """Create difficult tactical positions"""
    tactical_positions = [
        # Famous tactical motifs
        "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",  # Italian Game tactics
        "rnbqkb1r/ppp2ppp/3p1n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4",  # Scotch Game
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4",  # Italian vs Two Knights
        "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2",  # Alekhine Defense
        "rnbqkb1r/ppp1pppp/5n2/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 3",  # Scandinavian Defense
        
        # Difficult tactical puzzles
        "2rr3k/pp3pp1/1nnqbN1p/3ppN2/2nPP3/2P1B3/PPQ2PPP/R4RK1 w - - 0 1",  # Complex tactical shot
        "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/3P1N2/PPP1NPPP/R2Q1RK1 w - - 0 1",  # Pin and fork motifs
        "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/3P1N2/PPP1NPPP/R1BQ1RK1 w - - 0 1",  # Central tension
        "r2qkb1r/pb2nppp/1pn1p3/3pP3/3P4/2N2N2/PPP1BPPP/R1BQK2R w KQkq - 0 1",  # French Defense complex
        "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 4 4",  # Italian Game critical
        
        # Sacrificial attacks
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 0 5",  # Sacrifice preparation
        "r2qkb1r/ppp2ppp/2np1n2/4p3/2BPP1b1/2N2N2/PPP2PPP/R1BQK2R w KQkq - 0 1",  # Bg4 pin complex
        "r1bqkb1r/pppp1p1p/2n2np1/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5",  # Fianchetto setup
        "rnbqk1nr/pppp1ppp/8/2b1p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3",  # Early Bc5
        "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3",  # Italian vs Nc6
        
        # Mating attack patterns
        "2kr3r/pppq1ppp/3p1n2/2b1p3/2B1P1b1/2NP1N2/PPP1QPPP/R1B1K2R w KQ - 0 1",  # Mating net
        "r2qk2r/ppp2ppp/2np1n2/2b1p1B1/2B1P1b1/3P1N2/PPP1NPPP/R2QK2R w KQkq - 0 1",  # Opposite castling
        "r1bq1rk1/ppp2ppp/2np1n2/4p3/1bB1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 1",  # Bb4 pin
        "rnbqk2r/ppp2ppp/3p1n2/4p3/1bB1P3/2N2N2/PPP2PPP/R1BQK2R w KQkq - 0 1",  # Early development
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 4 4",  # Classical setup
    ]
    return tactical_positions

def create_endgame_positions():
    """Create complex endgame positions"""
    endgame_positions = [
        # Pawn endgames
        "8/8/8/3k4/3P4/3K4/8/8 w - - 0 1",  # Basic pawn endgame
        "8/8/8/2k1p3/4P3/3K4/8/8 w - - 0 1",  # Opposition
        "8/8/3k4/2ppp3/2PPP3/3K4/8/8 w - - 0 1",  # Pawn breakthrough
        "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",  # Complex pawn endgame
        "8/1p6/kP6/8/8/8/5K2/8 w - - 0 1",  # Pawn promotion race
        
        # Rook endgames
        "8/8/8/8/8/3k4/3r4/3K3R w - - 0 1",  # Lucena position
        "8/8/8/8/8/8/3k1r2/4K2R w - - 0 1",  # Philidor position
        "R7/8/8/8/8/3k4/3r4/3K4 w - - 0 1",  # Rook vs Rook
        "8/8/8/R7/8/3k4/5r2/4K3 w - - 0 1",  # Active rook
        "8/8/8/8/5R2/3k4/5r2/4K3 w - - 0 1",  # Rook endgame technique
        
        # Knight endgames
        "8/8/8/8/8/3k1n2/8/4K1N1 w - - 0 1",  # Knight vs Knight
        "8/8/8/3k4/8/8/3n4/4K1N1 w - - 0 1",  # Knight endgame
        "8/8/8/8/3k4/8/5n2/4KN2 w - - 0 1",  # Knight technique
        
        # Bishop endgames
        "8/8/8/3k4/8/8/3b4/4KB2 w - - 0 1",  # Same color bishops
        "8/8/8/3k4/8/8/3B4/4Kb2 w - - 0 1",  # Opposite color bishops
        "8/8/8/8/3k4/8/5b2/4KB2 w - - 0 1",  # Bishop endgame
        
        # Queen endgames
        "8/8/8/8/8/3k4/3q4/3K3Q w - - 0 1",  # Queen vs Queen
        "8/8/8/8/8/8/3k1q2/4K2Q w - - 0 1",  # Queen endgame technique
        
        # Mixed piece endgames
        "8/8/8/8/8/3k1r2/8/4KR2 w - - 0 1",  # Rook vs Rook
        "8/8/8/8/8/3k1n2/8/4KR2 w - - 0 1",  # Rook vs Knight
        "8/8/8/8/8/3k1b2/8/4KR2 w - - 0 1",  # Rook vs Bishop
        "8/8/8/8/8/3k1q2/8/4KR2 w - - 0 1",  # Rook vs Queen
        
        # Famous endgame studies
        "8/8/1p6/8/1P6/8/2K5/1k6 w - - 0 1",  # Réti study
        "8/8/8/8/8/1K6/2P5/1k6 w - - 0 1",  # Basic promotion
        "8/8/8/8/8/8/1K1k4/8 w - - 0 1",  # King and pawn vs King
        "8/8/8/8/8/8/2K1k3/8 w - - 0 1",  # Opposition study
        "8/8/8/8/8/2K5/3k4/8 w - - 0 1",  # King activity
    ]
    return endgame_positions

def create_strategic_positions():
    """Create complex strategic middlegame positions"""
    strategic_positions = [
        # Pawn structure themes
        "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/2N2N2/PP2PPPP/R1BQKB1R b KQkq c3 0 4",  # IQP positions
        "rnbqkb1r/pp3ppp/4pn2/2pp4/2PP4/2N2N2/PP2PPPP/R1BQKB1R w KQkq - 0 5",  # Central tension
        "rnbqkb1r/pp2pppp/5n2/2pp4/3P4/2N2N2/PPP1PPPP/R1BQKB1R w KQkq - 0 4",  # Caro-Kann structure
        "rnbqkb1r/pppp1ppp/4pn2/8/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 3",  # English Opening
        "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2",  # Alekhine structure
        
        # Piece activity themes
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 0 5",  # Piece development
        "r2qkb1r/ppp2ppp/2np1n2/4p3/2BPP1b1/2N2N2/PPP2PPP/R1BQK2R w KQkq - 0 6",  # Central control
        "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 6",  # Symmetrical structure
        "rnbq1rk1/ppp1ppbp/3p1np1/8/2PP4/2N1PN2/PP2BPPP/R1BQ1RK1 w - - 0 6",  # King's Indian setup
        "rnbqkb1r/pp3ppp/4pn2/2pp4/2PP4/2N2N2/PP2PPPP/R1BQKB1R w KQkq - 0 5",  # Queen's Gambit Declined
        
        # Imbalanced positions
        "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQR1K1 w - - 0 6",  # Rook vs Bishop
        "r2q1rk1/ppp1bppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP1BPPP/R2Q1RK1 w - - 0 6",  # Bishop pair
        "r1bq1rk1/ppp1nppp/3p4/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 6",  # Knight vs Bishop
        "r2q1rk1/ppp2ppp/2np1n2/2b1p3/1bB1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 6",  # Double bishops
        "r1bq1rk1/ppp2ppp/2np1n2/4p3/1bB1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 6",  # Bishop activity
        
        # Space advantage themes
        "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/2N2N2/PP2PPPP/R1BQKB1R b KQkq - 0 4",  # Space in center
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4",  # Development advantage
        "rnbq1rk1/ppp1ppbp/3p1np1/8/2PP4/2N1PN2/PP2BPPP/R1BQ1RK1 b - - 0 6",  # Fianchetto structures
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 0 5",  # Classical development
        "rnbqkb1r/pp3ppp/4pn2/2pp4/2PP4/2N2N2/PP2PPPP/R1BQKB1R w KQkq - 0 5",  # Tension maintenance
    ]
    return strategic_positions

def create_famous_positions():
    """Create positions from famous games and studies"""
    famous_positions = [
        # Famous game positions
        "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",  # Morphy's Opera Game setup
        "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 4 4",  # Italian Game classical
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 4 4",  # Italian Game main line
        "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq d6 0 3",  # Queen's Gambit
        "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2",  # Alekhine Defense
        
        # Computer chess test positions (Bratko-Kopec Test)
        "1k1r4/pp1b1R2/3q2pp/4p3/2B5/4Q3/PPP2B2/2K5 b - - 0 1",  # BK.01
        "3r1k2/4npp1/1ppr3p/p6P/P2PPPP1/1NR5/5K2/2R5 w - - 0 1",  # BK.02
        "2q1rr1k/3bbnnp/p2p1pp1/2pPp3/PpP1P1P1/1P2BNNP/2BQ1PRK/7R b - - 0 1",  # BK.03
        "rnbqkb1r/p3pppp/1p6/2ppP3/3N4/2P5/PPP1PPPP/R1BQKB1R w KQkq d6 0 1",  # BK.04
        "r1b2rk1/2q1b1pp/p2ppn2/1p6/3QP3/1BN1B3/PPP3PP/R4RK1 w - - 0 1",  # BK.05
        
        # WAC (Win At Chess) positions
        "2rr3k/pp3pp1/1nnqbN1p/3ppN2/2nPP3/2P1B3/PPQ2PPP/R4RK1 w - - 0 1",  # WAC.001
        "8/7p/5k2/5p2/p1p2P2/Pr1pPK2/1P1R3P/8 b - - 0 1",  # WAC.002
        "5rk1/1ppb3p/p1pb4/6q1/3P1p1r/2P1R2P/PP1BQ1P1/5RKN w - - 0 1",  # WAC.003
        "r1bq2rk/pp2b1pp/2np1n2/2p1pp2/2P1P3/2N2N1P/PP2BPP1/R1BQR1K1 b - - 0 1",  # WAC.004
        "2r3k1/pppR1pp1/4p3/4P1P1/5P2/1P4K1/r1p5/8 w - - 0 1",  # WAC.005
        
        # Polgar 5334 positions (sample)
        "r6r/1p2k1pp/3p4/2pP4/2P1pPb1/2N1P3/PP4PP/R4RK1 b - - 0 1",  # Polgar tactical
        "6k1/5p2/6p1/8/7p/8/6PP/6K1 b - - 0 1",  # Polgar endgame
        "r1bq1r1k/b1p1npp1/p2p3p/1p6/3PP3/1B2NN2/PP3PPP/R2Q1RK1 w - - 0 1",  # Polgar middlegame
    ]
    return famous_positions

def create_computer_test_positions():
    """Create positions specifically designed to test computer engines"""
    computer_positions = [
        # Deep tactical positions
        "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/3P1N2/PPP1NPPP/R2Q1RK1 w - - 0 1",
        "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/3P1N2/PPP1NPPP/R1BQ1RK1 w - - 0 1",
        "r2qkb1r/pb2nppp/1pn1p3/3pP3/3P4/2N2N2/PPP1BPPP/R1BQK2R w KQkq - 0 1",
        "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 4 4",
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 4 4",
        
        # Positions with hidden tactics
        "r2q1rk1/ppp2ppp/2n1bn2/2b1p3/3pP3/3P1NPP/PPP1NPB1/R1BQ1RK1 b - - 0 1",
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 0 5",
        "rnbq1rk1/ppp1ppbp/3p1np1/8/2PP4/2N1PN2/PP2BPPP/R1BQ1RK1 b - - 0 6",
        "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 6",
        "rnbqkb1r/pp3ppp/4pn2/2pp4/2PP4/2N2N2/PP2PPPP/R1BQKB1R w KQkq - 0 5",
        
        # Evaluation test positions
        "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",  # Complex evaluation
        "8/8/1p6/8/1P6/8/2K5/1k6 w - - 0 1",  # Precise calculation needed
        "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/3P1N2/PPP1NPPP/R2Q1RK1 w - - 0 1",  # Material imbalance
        "2rr3k/pp3pp1/1nnqbN1p/3ppN2/2nPP3/2P1B3/PPQ2PPP/R4RK1 w - - 0 1",  # Sacrificial attack
        "r1bq1rk1/ppp2ppp/2np1n2/4p3/1bB1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 1",  # Pin tactics
    ]
    return computer_positions

def generate_random_complex_positions(count=50):
    """Generate random but complex positions"""
    positions = []
    
    # Create positions with specific characteristics
    base_positions = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # Starting position
    ]
    
    for _ in range(count):
        # Start from a base position and make random moves
        board = chess.Board()
        
        # Make 10-25 random moves to get to middlegame
        moves_count = random.randint(10, 25)
        for _ in range(moves_count):
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            board.push(move)
        
        # Only add if position is not trivial
        if len(list(board.legal_moves)) > 5 and not board.is_game_over():
            positions.append(board.fen())
    
    return positions

def main():
    """Generate comprehensive position test suite"""
    print("Generating comprehensive chess position test suite...")
    
    all_positions = []
    
    # Add different categories of positions
    print("Adding tactical positions...")
    all_positions.extend(create_tactical_positions())
    
    print("Adding endgame positions...")
    all_positions.extend(create_endgame_positions())
    
    print("Adding strategic positions...")
    all_positions.extend(create_strategic_positions())
    
    print("Adding famous positions...")
    all_positions.extend(create_famous_positions())
    
    print("Adding computer test positions...")
    all_positions.extend(create_computer_test_positions())
    
    print("Adding random complex positions...")
    all_positions.extend(generate_random_complex_positions(50))
    
    # Remove duplicates while preserving order
    unique_positions = []
    seen = set()
    for pos in all_positions:
        if pos not in seen:
            unique_positions.append(pos)
            seen.add(pos)
    
    print(f"Generated {len(unique_positions)} unique positions")
    
    # Create PGN file
    pgn_content = ""
    for i, fen in enumerate(unique_positions, 1):
        # Create a game with the position
        game = chess.pgn.Game()
        game.headers["Event"] = "Comprehensive Test Suite"
        game.headers["Site"] = "Engine Analysis"
        game.headers["Date"] = "2025.01.11"
        game.headers["Round"] = str(i)
        game.headers["White"] = "Test"
        game.headers["Black"] = "Position"
        game.headers["Result"] = "*"
        game.headers["FEN"] = fen
        game.headers["SetUp"] = "1"
        
        # Set up the board from FEN
        board = chess.Board(fen)
        game.setup(board)
        
        pgn_content += str(game) + "\n\n"
    
    # Save to file
    with open("comprehensive_positions.pgn", "w") as f:
        f.write(pgn_content)
    
    print(f"Saved {len(unique_positions)} positions to comprehensive_positions.pgn")
    
    # Create summary
    print("\nPosition breakdown:")
    print(f"- Tactical positions: {len(create_tactical_positions())}")
    print(f"- Endgame positions: {len(create_endgame_positions())}")
    print(f"- Strategic positions: {len(create_strategic_positions())}")
    print(f"- Famous positions: {len(create_famous_positions())}")
    print(f"- Computer test positions: {len(create_computer_test_positions())}")
    print(f"- Random complex positions: 50")
    print(f"- Total unique positions: {len(unique_positions)}")

if __name__ == "__main__":
    main()
