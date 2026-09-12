"""
Positional evaluation and minimax search engine with alpha-beta pruning.
Acts as a high-performance evaluation fallback if external UCI binaries are unavailable.
"""

import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 335,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

PAWN_TABLE = [
    0,   0,   0,   0,   0,   0,   0,   0,
    50,  50,  50,  50,  50,  50,  50,  50,
    10,  10,  20,  30,  30,  20,  10,  10,
    5,   5,  10,  27,  27,  10,   5,   5,
    0,   0,   0,  25,  25,   0,   0,   0,
    5,  -5, -10,   0,   0, -10,  -5,   5,
    5,  10,  10, -25, -25,  10,  10,   5,
    0,   0,   0,   0,   0,   0,   0,   0
]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   5,  20,  25,  25,  20,   5, -30,
    -30,   5,  20,  25,  25,  20,   5, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   0,  10,  15,  15,  10,   0, -10,
    -10,   5,  10,  15,  15,  10,   5, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

ROOK_TABLE = [
      0,   0,   0,   5,   5,   0,   0,   0,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
      5,  10,  10,  10,  10,  10,  10,   5,
      0,   0,   0,   0,   0,   0,   0,   0
]

QUEEN_TABLE = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -10,   5,   5,   5,   5,   5,   0, -10,
      0,   0,   5,   5,   5,   5,   0,  -5,
     -5,   0,   5,   5,   5,   5,   0,  -5,
    -10,   0,   5,   5,   5,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20
]

KING_MIDDLE_TABLE = [
     20,  30,  10,   0,   0,  10,  30,  20,
     20,  20,   0,   0,   0,   0,  20,  20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]


def evaluate_board(board: chess.Board) -> int:
    """Evaluates the board position from the perspective of White."""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        value = PIECE_VALUES[piece.piece_type]
        is_white = (piece.color == chess.WHITE)
        sq_idx = square if is_white else chess.square_mirror(square)

        # Positional piece-square table additions
        if piece.piece_type == chess.PAWN:
            value += PAWN_TABLE[sq_idx]
        elif piece.piece_type == chess.KNIGHT:
            value += KNIGHT_TABLE[sq_idx]
        elif piece.piece_type == chess.BISHOP:
            value += BISHOP_TABLE[sq_idx]
        elif piece.piece_type == chess.ROOK:
            value += ROOK_TABLE[sq_idx]
        elif piece.piece_type == chess.QUEEN:
            value += QUEEN_TABLE[sq_idx]
        elif piece.piece_type == chess.KING:
            value += KING_MIDDLE_TABLE[sq_idx]

        if is_white:
            score += value
        else:
            score -= value

    return score


def move_score(board: chess.Board, move: chess.Move) -> int:
    """Heuristic move ordering: captures and promotions first."""
    score = 0
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        victim_val = PIECE_VALUES[victim.piece_type] if victim else 100
        attacker_val = PIECE_VALUES[attacker.piece_type] if attacker else 100
        score += 1000 + (victim_val - attacker_val // 10)

    if move.promotion:
        score += 800

    if board.gives_check(move):
        score += 300

    return score


def quiescence(board: chess.Board, alpha: int, beta: int, depth: int = 2) -> int:
    """Quiescence search to evaluate tactical capture chains."""
    stand_pat = evaluate_board(board) if board.turn == chess.WHITE else -evaluate_board(board)

    if depth == 0 or board.is_game_over():
        return stand_pat

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    capture_moves = [m for m in board.legal_moves if board.is_capture(m)]
    capture_moves.sort(key=lambda m: move_score(board, m), reverse=True)

    for move in capture_moves:
        board.push(move)
        score = -quiescence(board, -beta, -alpha, depth - 1)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def alpha_beta_search(board: chess.Board, depth: int, alpha: int, beta: int, is_maximizing: bool) -> int:
    """Alpha-beta negamax search."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    moves = list(board.legal_moves)
    moves.sort(key=lambda m: move_score(board, m), reverse=True)

    if is_maximizing:
        max_eval = -float('inf')
        for move in moves:
            board.push(move)
            eval_score = alpha_beta_search(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            board.push(move)
            eval_score = alpha_beta_search(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def find_best_fallback_move(board: chess.Board, depth: int = 3) -> chess.Move:
    """Calculates the best move using alpha-beta search and heuristic safety."""
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    legal_moves.sort(key=lambda m: move_score(board, m), reverse=True)

    is_white = (board.turn == chess.WHITE)
    best_move = legal_moves[0]
    best_val = -float('inf') if is_white else float('inf')

    for move in legal_moves:
        board.push(move)
        score = alpha_beta_search(board, depth - 1, -float('inf'), float('inf'), not is_white)
        board.pop()

        if is_white:
            if score > best_val:
                best_val = score
                best_move = move
        else:
            if score < best_val:
                best_val = score
                best_move = move

    return best_move
