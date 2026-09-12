"""
Master Opening Book Repertoire for Dave Christopher Chess Engine (2000 ELO).
Includes classical, semi-open, closed, and flank opening variations.
"""

import random

OPENING_BOOK = {
    # Starting position
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": ["e2e4", "d2d4", "c2c4", "g1f3"],

    # Responses to 1. e4
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -": ["c7c5", "e7e5", "e7e6", "c7c6", "d7d5"],
    
    # Responses to 1. d4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq -": ["g8f6", "d7d5", "e7e6", "f7f5", "c7c5"],

    # Responses to 1. c4 (English Opening)
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq -": ["e7e5", "c7c5", "g8f6", "e7e6"],

    # Responses to 1. Nf3 (Reti Opening)
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq -": ["d7d5", "g8f6", "c7c5", "e7e6"],

    # --- SICILIAN DEFENSE ---
    # 1. e4 c5 2. Nf3
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -": ["d7d6", "e7e6", "b8c6", "g7g6"],
    # 2... d6 3. d4
    "rnbqkbnr/pp2pppp/3p4/2p5/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq -": ["c5d4"],
    # 3... cxd4 4. Nxd4 Nf6
    "rnbqkbnr/pp2pppp/3p4/8/3NP3/8/PPP2PPP/RNBQKB1R b KQkq -": ["g8f6"],
    # 4... Nf6 5. Nc3
    "rnbqkb1r/pp2pppp/3p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R b KQkq -": ["a7a6", "g7g6", "e7e6", "b8c6"], # Najdorf, Dragon, Scheveningen, Classical
    # Najdorf 5... a6 6. Be2 / Bg5 / Be3
    "rnbqkb1r/1p2pppp/p2p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq -": ["f1e2", "c1g5", "c1e3", "f2f4"],

    # --- OPEN GAME (1. e4 e5) ---
    # 1. e4 e5 2. Nf3
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -": ["b8c6", "g8f6", "d7d6"],
    # 2... Nc6 3. Bb5 (Ruy Lopez)
    "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq -": ["a7a6", "g8f6", "f8c5", "d7d6"],
    # 3... a6 4. Ba4
    "r1bqkbnr/1ppp1ppp/p1n5/4p3/B3P3/5N2/PPPP1PPP/RNBQK2R b KQkq -": ["g8f6", "b7b5", "f8c5"],
    # 4... Nf6 5. O-O
    "r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQ1RK1 b kq -": ["f8e7", "b7b5", "f6e4"],
    # 2... Nc6 3. Bc4 (Italian Game)
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq -": ["f8c5", "g8f6", "d7d6"],
    # 3... Bc5 4. c3
    "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/2P2N2/PP1P1PPP/RNBQK2R b KQkq -": ["g8f6", "d7d6", "d8e7"],

    # --- FRENCH DEFENSE ---
    # 1. e4 e6 2. d4 d5
    "rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq -": ["b1c3", "e4e5", "b1d2", "e4d5"],
    # Advance Variation 3. e5 c5
    "rnbqkbnr/ppp2ppp/4p3/3pP3/3P4/8/PPP2PPP/RNBQKBNR b KQkq -": ["c7c5", "c8d7"],

    # --- CARO-KANN DEFENSE ---
    # 1. e4 c6 2. d4 d5
    "rnbqkbnr/pp2pppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq -": ["b1c3", "e4e5", "e4d5"],
    # Classical 3. Nc3 dxe4 4. Nxe4
    "rnbqkbnr/pp2pppp/2p5/8/3PN3/8/PPP2PPP/R1BQKBNR b KQkq -": ["c8f5", "b8d7", "g8f6"],

    # --- SCANDINAVIAN DEFENSE ---
    # 1. e4 d5 2. exd5
    "rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq -": ["d8d5", "g8f6"],

    # --- QUEEN'S GAMBIT (1. d4 d5 2. c4) ---
    "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq -": ["e7e6", "c7c6", "d5c4", "g8f6"], # QGD, Slav, QGA
    # 2... e6 3. Nc3 Nf6
    "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq -": ["c1g5", "g1f3", "c4d5"],
    # 2... c6 3. Nf3 Nf6 4. Nc3
    "rnbqkb1r/pp2pppp/2p2n2/3p4/2PP4/2N2N2/PP2PPPP/R1BQKB1R b KQkq -": ["d5c4", "e7e6"],

    # --- KING'S INDIAN & GRUNFELD ---
    # 1. d4 Nf6 2. c4 g6 3. Nc3
    "rnbqkb1r/pppppp1p/5np1/8/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq -": ["f8g7", "d7d5"], # KID, Grunfeld
    # 3... Bg7 4. e4 d6
    "rnbqk2r/ppp1ppbp/3p1np1/8/2PPP3/2N5/PP3PPP/R1BQKBNR w KQkq -": ["g1f3", "f2f3", "f1e2"],

    # --- NIMZO-INDIAN DEFENSE ---
    # 1. d4 Nf6 2. c4 e6 3. Nc3 Bb4
    "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N5/PP2PPPP/R1BQKBNR w KQkq -": ["e2e3", "d1c2", "g1f3", "a2a3"],

    # --- ENGLISH OPENING ---
    # 1. c4 e5 2. Nc3
    "rnbqkbnr/pppp1ppp/8/4p3/2P5/2N5/PP1PPPPP/R1BQKBNR b KQkq -": ["g8f6", "b8c6", "f8b4", "g7g6"],
}


def get_book_move(fen: str) -> str:
    """Returns a book move in UCI notation (e.g. 'e2e4') if found."""
    # Match FEN by board squares + turn + castling rights
    normalized_fen = " ".join(fen.split()[:3])

    for book_fen, moves in OPENING_BOOK.items():
        book_norm = " ".join(book_fen.split()[:3])
        if normalized_fen == book_norm:
            return random.choice(moves)

    return None
