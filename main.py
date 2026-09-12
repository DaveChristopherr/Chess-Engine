#!/usr/bin/env python3
"""
Dave Christopher Chess Engine (2000 ELO) — Interactive Terminal Game
Allows playing directly against the 2000 ELO engine in your terminal.
"""

import sys
import os
import time
import chess

# Add backend directory to module search path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from engine import select_best_move
from board import render_ascii_board, get_game_status_summary


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(player_is_white: bool):
    print("=" * 50)
    print("  DAVE CHRISTOPHER CHESS ENGINE (2000 ELO)")
    print("=" * 50)
    print(f"  You: {'White (moves first)' if player_is_white else 'Black'}")
    print(f"  Dave: {'Black' if player_is_white else 'White (moves first)'}")
    print("  Type your move in SAN (e.g. e4, Nf3, O-O) or UCI (e2e4)")
    print("  Type 'quit' to exit, 'resign' to concede.")
    print("-" * 50)


def parse_user_move(board: chess.Board, move_text: str):
    """Attempts to parse user input as SAN or UCI move."""
    clean = move_text.strip()
    # Try SAN
    try:
        return board.parse_san(clean)
    except ValueError:
        pass
    # Try UCI
    try:
        m = chess.Move.from_uci(clean)
        if m in board.legal_moves:
            return m
    except ValueError:
        pass
    return None


def play_game():
    clear_screen()
    print("=" * 50)
    print("  WELCOME TO DAVE CHRISTOPHER CHESS (2000 ELO)")
    print("=" * 50)
    
    choice = input("\nPlay as White (w) or Black (b)? [default: w]: ").strip().lower()
    player_is_white = choice != "b"

    board = chess.Board()

    while not board.is_game_over():
        clear_screen()
        print_header(player_is_white)
        print(render_ascii_board(board, flipped=not player_is_white))
        print("\n" + get_game_status_summary(board))
        print(f"FEN: {board.fen()}\n")

        is_player_turn = (board.turn == chess.WHITE and player_is_white) or (board.turn == chess.BLACK and not player_is_white)

        if is_player_turn:
            while True:
                user_input = input("Your move: ").strip()
                if user_input.lower() in ("quit", "exit"):
                    print("Game aborted.")
                    return
                if user_input.lower() == "resign":
                    print("You resigned. Dave Christopher wins!")
                    return

                move = parse_user_move(board, user_input)
                if move:
                    board.push(move)
                    break
                else:
                    print("Invalid move! Use SAN (e.g. e4, Nf3) or UCI (e2e4).")
        else:
            print("Dave Christopher is thinking...")
            t0 = time.time()
            res = select_best_move(board.fen(), target_elo=2000, time_limit=0.20)
            elapsed = round(time.time() - t0, 3)

            if not res or not res.get("from") or not res.get("to"):
                print("Engine could not find a move.")
                break

            uci_str = res["from"] + res["to"] + (res.get("promotion") or "")
            bot_move = chess.Move.from_uci(uci_str)
            san_str = board.san(bot_move)
            board.push(bot_move)
            print(f"Dave played: {san_str} ({res.get('source')}, {elapsed}s)")
            time.sleep(0.5)

    clear_screen()
    print_header(player_is_white)
    print(render_ascii_board(board, flipped=not player_is_white))
    print("\n=== GAME OVER ===")
    print(get_game_status_summary(board))


if __name__ == "__main__":
    play_game()
