#!/usr/bin/env python3
"""
Dave Christopher Chess Engine — Main Engine Bridge
Provides 2000 ELO chess move generation via Stockfish UCI with pure-Python search fallback.
"""

import sys
import json
import os
import chess
import chess.engine

# Allow loading local modules regardless of current working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openings import get_book_move
from evaluator import find_best_fallback_move
from search import search_best_move

STOCKFISH_SEARCH_PATHS = [
    os.environ.get("STOCKFISH_PATH", ""),
    "/usr/games/stockfish",
    "/usr/bin/stockfish",
    "/usr/local/bin/stockfish",
    "stockfish"
]


def get_stockfish_path():
    """Finds available Stockfish binary in common system locations."""
    for path in STOCKFISH_SEARCH_PATHS:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def select_best_move(fen: str, target_elo: int = 2000, time_limit: float = 0.18):
    """Computes the optimal move for the given FEN position."""
    board = chess.Board(fen)

    if board.is_game_over():
        return None

    # 1. Opening Book
    book_move = get_book_move(fen)
    if book_move:
        try:
            move_obj = chess.Move.from_uci(book_move)
            if move_obj in board.legal_moves:
                san = board.san(move_obj)
                return {
                    "from": chess.square_name(move_obj.from_square),
                    "to": chess.square_name(move_obj.to_square),
                    "promotion": chess.piece_symbol(move_obj.promotion).lower() if move_obj.promotion else None,
                    "san": san,
                    "source": "book"
                }
        except Exception:
            pass

    # 2. Stockfish UCI at 2000 ELO
    stockfish_bin = get_stockfish_path()
    if stockfish_bin:
        try:
            engine = chess.engine.SimpleEngine.popen_uci(stockfish_bin)
            try:
                engine.configure({
                    "UCI_LimitStrength": True,
                    "UCI_Elo": target_elo
                })
            except Exception:
                pass

            result = engine.play(board, chess.engine.Limit(time=time_limit))
            engine.quit()

            if result and result.move:
                best_move = result.move
                san = board.san(best_move)
                return {
                    "from": chess.square_name(best_move.from_square),
                    "to": chess.square_name(best_move.to_square),
                    "promotion": chess.piece_symbol(best_move.promotion).lower() if best_move.promotion else None,
                    "san": san,
                    "source": "stockfish_2000"
                }
        except Exception as err:
            sys.stderr.write(f"Stockfish execution warning: {err}\n")

    # 3. Iterative Deepening Alpha-Beta Search with Transposition Tables
    try:
        search_move = search_best_move(board, max_depth=4, time_limit=time_limit)
        if search_move:
            san = board.san(search_move)
            return {
                "from": chess.square_name(search_move.from_square),
                "to": chess.square_name(search_move.to_square),
                "promotion": chess.piece_symbol(search_move.promotion).lower() if search_move.promotion else None,
                "san": san,
                "source": "python_search_engine"
            }
    except Exception as err:
        sys.stderr.write(f"Search engine warning: {err}\n")

    # 4. Positional Minimax Fallback
    fallback_move = find_best_fallback_move(board, depth=3)
    if fallback_move:
        san = board.san(fallback_move)
        return {
            "from": chess.square_name(fallback_move.from_square),
            "to": chess.square_name(fallback_move.to_square),
            "promotion": chess.piece_symbol(fallback_move.promotion).lower() if fallback_move.promotion else None,
            "san": san,
            "source": "minimax_evaluator"
        }

    # 5. Final safety guard
    legal_moves = list(board.legal_moves)
    if legal_moves:
        first = legal_moves[0]
        return {
            "from": chess.square_name(first.from_square),
            "to": chess.square_name(first.to_square),
            "promotion": None,
            "san": board.san(first),
            "source": "legal_fallback"
        }

    return None


def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input:
            print(json.dumps({"error": "No input provided"}))
            return

        payload = json.loads(raw_input)
        fen = payload.get("fen", chess.STARTING_FEN)
        target_elo = int(payload.get("elo", 2000))
        time_limit = float(payload.get("timeLimit", 0.18))

        best = select_best_move(fen=fen, target_elo=target_elo, time_limit=time_limit)
        print(json.dumps(best or {}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    main()
