"""
Board utility helpers for Dave Christopher Chess Engine.
Provides FEN parsing, coordinate manipulation, and terminal ASCII board visualizer.
"""

import chess

UNICODE_PIECE_SYMBOLS = {
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙",
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    ".": "·"
}


def render_ascii_board(board: chess.Board, flipped: bool = False) -> str:
    """Renders retro ASCII terminal representation of the chess board."""
    lines = []
    lines.append("  +-----------------+")
    ranks = range(8) if flipped else range(7, -1, -1)
    files = range(7, -1, -1) if flipped else range(8)

    for rank in ranks:
        row_str = f"{rank + 1} |"
        for file in files:
            sq = chess.square(file, rank)
            piece = board.piece_at(sq)
            sym = piece.symbol() if piece else "."
            row_str += f" {UNICODE_PIECE_SYMBOLS.get(sym, sym)}"
        row_str += " |"
        lines.append(row_str)

    lines.append("  +-----------------+")
    file_labels = "    h g f e d c b a" if flipped else "    a b c d e f g h"
    lines.append(file_labels)
    return "\n".join(lines)


def get_game_status_summary(board: chess.Board) -> str:
    """Returns human-readable game state status string."""
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"Checkmate! {winner} wins."
    if board.is_stalemate():
        return "Stalemate. Draw game."
    if board.is_insufficient_material():
        return "Draw by insufficient material."
    if board.can_claim_threefold_repetition():
        return "Draw available by threefold repetition."
    if board.can_claim_fifty_moves():
        return "Draw available by 50-move rule."
    if board.is_check():
        turn = "White" if board.turn == chess.WHITE else "Black"
        return f"Check on {turn}!"
    return "In progress."
