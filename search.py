"""
Search algorithms for Dave Christopher Chess Engine.
Features Alpha-Beta Pruning, Quiescence Search, Move Ordering (MVV-LVA), and Transposition Tables.
"""

import time
import chess
from evaluator import evaluate_board, PIECE_VALUES
from transposition import TranspositionTable

tt = TranspositionTable(size_mb=16)

# MVV-LVA (Most Valuable Victim - Least Valuable Attacker) capture priority matrix
VICTIM_SCORES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 350,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 10000
}


def score_move(board: chess.Board, move: chess.Move, hash_move=None) -> int:
    """Assigns priority score to a move to maximize alpha-beta pruning cutoff rate."""
    if hash_move and move == hash_move:
        return 200000

    score = 0
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        v_val = VICTIM_SCORES.get(victim.piece_type, 100) if victim else 100
        a_val = VICTIM_SCORES.get(attacker.piece_type, 100) if attacker else 100
        score += 10000 + (v_val * 10 - a_val)

    if move.promotion:
        score += 9000

    if board.gives_check(move):
        score += 3000

    # Discourage moving king in middle game unless castling
    if board.is_castling(move):
        score += 2000

    return score


def order_moves(board: chess.Board, hash_move=None):
    """Sorts legal moves using MVV-LVA and positional heuristics."""
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: score_move(board, m, hash_move), reverse=True)
    return moves


def quiescence_search(board: chess.Board, alpha: int, beta: int, depth: int = 4) -> int:
    """Evaluates capture sequences to prevent the horizon effect in tactical positions."""
    stand_pat = evaluate_board(board) if board.turn == chess.WHITE else -evaluate_board(board)

    if depth == 0 or board.is_game_over():
        return stand_pat

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    captures = [m for m in board.legal_moves if board.is_capture(m) or m.promotion]
    captures.sort(key=lambda m: score_move(board, m), reverse=True)

    for move in captures:
        board.push(move)
        score = -quiescence_search(board, -beta, -alpha, depth - 1)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def alpha_beta(board: chess.Board, depth: int, alpha: int, beta: int, deadline: float = None) -> tuple:
    """Negamax Alpha-Beta search with Transposition Table caching."""
    if deadline and time.time() > deadline:
        return evaluate_board(board) if board.turn == chess.WHITE else -evaluate_board(board), None

    zkey = tt.compute_hash(board)
    cached_score, hash_move = tt.probe(zkey, depth, alpha, beta)
    if cached_score is not None:
        return cached_score, hash_move

    if depth <= 0 or board.is_game_over():
        score = quiescence_search(board, alpha, beta)
        return score, None

    orig_alpha = alpha
    best_move = None
    best_score = -float('inf')

    ordered = order_moves(board, hash_move)
    for move in ordered:
        board.push(move)
        score, _ = alpha_beta(board, depth - 1, -beta, -alpha, deadline)
        score = -score
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, score)
        if alpha >= beta:
            break

    # Store in transposition table
    if best_score <= orig_alpha:
        flag = TranspositionTable.UPPERBOUND
    elif best_score >= beta:
        flag = TranspositionTable.LOWERBOUND
    else:
        flag = TranspositionTable.EXACT

    tt.store(zkey, depth, best_score, flag, best_move)
    return best_score, best_move


def search_best_move(board: chess.Board, max_depth: int = 4, time_limit: float = 0.20) -> chess.Move:
    """Iterative deepening search engine respecting time constraints."""
    deadline = time.time() + time_limit
    best_move = None

    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
    if len(legal_moves) == 1:
        return legal_moves[0]

    for depth in range(1, max_depth + 1):
        if time.time() >= deadline:
            break
        score, move = alpha_beta(board, depth, -999999, 999999, deadline)
        if move is not None:
            best_move = move
        if abs(score) > 90000:  # Checkmate found
            break

    return best_move or legal_moves[0]
