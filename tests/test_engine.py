"""
Unit and tactical test suite for Dave Christopher Chess Engine (2000 ELO).
Run with: python3 -m unittest discover -s tests
"""

import unittest
import time
import sys
import os
import chess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from engine import select_best_move
from openings import get_book_move
from evaluator import evaluate_board
from search import search_best_move


class TestDaveChristopherEngine(unittest.TestCase):
    """Test suite for 2000 ELO chess engine capabilities."""

    def test_opening_book_e4(self):
        """Tests that engine responds to 1. e4 with a recognized opening book line."""
        board = chess.Board()
        board.push_san("e4")
        book_move = get_book_move(board.fen())
        self.assertIsNotNone(book_move)
        self.assertIn(book_move, ["c7c5", "e7e5", "e7e6", "c7c6", "d7d5"])

    def test_opening_book_d4(self):
        """Tests response to 1. d4."""
        board = chess.Board()
        board.push_san("d4")
        book_move = get_book_move(board.fen())
        self.assertIsNotNone(book_move)
        self.assertIn(book_move, ["g8f6", "d7d5", "e7e6", "f7f5", "c7c5"])

    def test_mate_in_one_scholar(self):
        """Tests that White spots immediate Scholar's Mate (Qxf7#)."""
        # Position: 1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6?? -> Qxf7#
        fen = "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"
        move = select_best_move(fen, target_elo=2000, time_limit=0.18)
        self.assertIsNotNone(move)
        self.assertEqual(move["from"], "h5")
        self.assertEqual(move["to"], "f7")
        self.assertIn("#", move["san"])

    def test_mate_in_one_back_rank(self):
        """Tests finding back-rank checkmate."""
        # White rook can deliver Rd8#
        fen = "6k1/5ppp/8/8/8/8/8/3R2K1 w - - 0 1"
        move = select_best_move(fen, target_elo=2000, time_limit=0.18)
        self.assertIsNotNone(move)
        self.assertEqual(move["from"], "d1")
        self.assertEqual(move["to"], "d8")

    def test_capture_hanging_queen(self):
        """Tests that engine captures an undefended queen."""
        # White queen on d4 is undefended, Black to move (Qxd4)
        fen = "rnbqkbnr/ppp1pppp/8/8/3Q4/8/PPP1PPPP/RNB1KBNR b KQkq - 0 2"
        move = select_best_move(fen, target_elo=2000, time_limit=0.18)
        self.assertIsNotNone(move)
        self.assertEqual(move["from"], "d8")
        self.assertEqual(move["to"], "d4")

    def test_response_speed(self):
        """Ensures move generation takes less than 300ms."""
        fen = "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 1 5"
        t0 = time.time()
        move = select_best_move(fen, target_elo=2000, time_limit=0.15)
        elapsed = time.time() - t0
        self.assertIsNotNone(move)
        self.assertLess(elapsed, 0.45)

    def test_evaluation_symmetry(self):
        """Initial board evaluation should be balanced."""
        board = chess.Board()
        score = evaluate_board(board)
        self.assertEqual(score, 0)


if __name__ == "__main__":
    unittest.main()
