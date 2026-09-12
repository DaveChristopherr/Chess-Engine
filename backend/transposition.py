"""
Zobrist Hashing and Transposition Table for Dave Christopher Chess Engine.
Provides high-speed caching for evaluated chess board positions.
"""

import random

# Fixed seed for deterministic Zobrist keys across sessions
random.seed(42)

# Generate 64-bit random integers for Zobrist hashing
# 64 squares x 12 piece types (6 white, 6 black)
PIECE_KEYS = {
    (piece_type, color, sq): random.getrandbits(64)
    for piece_type in range(1, 7)
    for color in (True, False)
    for sq in range(64)
}

SIDE_KEY = random.getrandbits(64)
CASTLE_KEYS = [random.getrandbits(64) for _ in range(16)]
EP_KEYS = [random.getrandbits(64) for _ in range(8)]


class TranspositionTable:
    """Fixed-capacity transposition table storing evaluation scores and depths."""

    EXACT = 0
    LOWERBOUND = 1
    UPPERBOUND = 2

    def __init__(self, size_mb: int = 16):
        # Calculate number of entries based on approximate memory limit
        self.entry_size = 32  # bytes approximately per entry
        self.capacity = (size_mb * 1024 * 1024) // self.entry_size
        self.table = {}

    def compute_hash(self, board) -> int:
        """Computes 64-bit Zobrist hash for a python-chess board."""
        zkey = 0
        for sq, piece in board.piece_map().items():
            zkey ^= PIECE_KEYS.get((piece.piece_type, piece.color, sq), 0)

        if not board.turn:
            zkey ^= SIDE_KEY

        castling_rights = (
            (1 if board.has_kingside_castling_rights(True) else 0)
            | (2 if board.has_queenside_castling_rights(True) else 0)
            | (4 if board.has_kingside_castling_rights(False) else 0)
            | (8 if board.has_queenside_castling_rights(False) else 0)
        )
        zkey ^= CASTLE_KEYS[castling_rights]

        if board.ep_square is not None:
            file_idx = board.ep_square % 8
            zkey ^= EP_KEYS[file_idx]

        return zkey

    def store(self, key: int, depth: int, score: int, flag: int, best_move=None):
        """Stores evaluation data into transposition table."""
        if len(self.table) >= self.capacity:
            # Simple eviction of oldest item if capacity is reached
            self.table.pop(next(iter(self.table)))

        self.table[key] = {
            "depth": depth,
            "score": score,
            "flag": flag,
            "best_move": best_move
        }

    def probe(self, key: int, depth: int, alpha: int, beta: int):
        """Probes transposition table for cached score or best move."""
        entry = self.table.get(key)
        if not entry:
            return None, None

        stored_move = entry.get("best_move")

        if entry["depth"] >= depth:
            score = entry["score"]
            if entry["flag"] == self.EXACT:
                return score, stored_move
            elif entry["flag"] == self.LOWERBOUND and score >= beta:
                return score, stored_move
            elif entry["flag"] == self.UPPERBOUND and score <= alpha:
                return score, stored_move

        return None, stored_move

    def clear(self):
        """Clears all stored transposition table entries."""
        self.table.clear()
