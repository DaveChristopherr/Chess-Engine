# Dave Christopher — 2000 ELO Chess Engine

A retro-styled, high-performance chess application featuring an authentic 2000 ELO Python chess engine, sub-second move generation, grandmaster opening repertoire, transposition tables, and an 8-bit CRT aesthetic with ambient rain effects.

![Language](https://img.shields.io/badge/language-Python-blue.svg)
![Rating](https://img.shields.io/badge/rating-2000%20ELO-green.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## About This Project

This is a personal hobby project that I created out of passion for chess programming and classic retro design. I originally began building this project back in 2025, but put it on hold for a while. I have now returned to completely overhaul, refactor, and finalize the codebase—ensuring clean separation of concerns, a dedicated Python engine with 2000 ELO capability, and a streamlined web and CLI experience.

---

## Features

- **Authentic 2000 ELO Engine**: Stockfish UCI integration with automated pure-Python minimax fallback, alpha-beta pruning, quiescence search, and piece-square evaluation.
- **Sub-Second Move Generation**: Bot moves execute in ~100ms to 200ms without freezing or lagging.
- **Grandmaster Opening Repertoire**: Instant book moves for Sicilian Defense (Najdorf, Dragon, Scheveningen), Ruy Lopez, Italian Game, French Defense, Caro-Kann, Queen's Gambit, King's Indian, and more.
- **Dual Modes (Web & Terminal CLI)**:
  - **Web GUI**: Retro pixel interface with coordinate labels, CRT scanlines, and animated particle rain.
  - **Terminal CLI**: Run `python3 main.py` to play against Dave Christopher directly in your terminal.
- **Transposition Table & Move Ordering**: 64-bit Zobrist hashing for caching positions, MVV-LVA capture ordering, and iterative deepening.
- **Tactical Move Hints**: Visual indicators for valid target squares and dashed highlights for captures.
- **Game Controls**: Full move history undo/redo, board flipping (play as White or Black), and resign.
- **Unit Test Suite**: 100% passing tests for opening lines, tactical checkmates, undefended pieces, and speed benchmarks.

---

## Project Structure

```
├── backend/
│   ├── engine.py          # Primary chess engine runner and UCI bridge
│   ├── search.py          # Alpha-beta negamax, quiescence & iterative deepening
│   ├── evaluator.py       # Positional piece-square evaluator & material heuristic
│   ├── openings.py        # Grandmaster opening book repertoire
│   ├── transposition.py   # 64-bit Zobrist hashing & transposition table
│   ├── board.py           # Pure Python board utilities & ASCII visualizer
│   └── server.py          # Standalone Python HTTP & API server
├── tests/
│   └── test_engine.py     # Python unittest suite for tactical & speed tests
├── public/                 # Static public assets (logos and avatars)
├── Dave Christopher Logo.png                          # Engine logo and favicon
├── 521174315.c110b96e.32x32o.c4d93e3c2fc2@2x.png      # Dave Christopher bot avatar
├── index.html             # Clean HTML presentation
├── style.css              # Retro pixel typography & CRT scanline styling
├── app.js                 # Vanilla frontend game loop & canvas animations
├── main.py                # Interactive CLI terminal game (Pure Python)
├── server.ts              # Web service bridge
├── package.json           # Node.js service config
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## Quick Start

### 1. Prerequisites

- **Python**: v3.10 or higher
- **Node.js**: v18.0.0 or higher
- **Stockfish** *(Optional but recommended for full 2000 ELO UCI performance)*:
  - Debian/Ubuntu: `sudo apt-get install stockfish`
  - macOS: `brew install stockfish`
  - Windows: Download binary from [Stockfish Official](https://stockfishchess.org/download/)

### 2. Install Dependencies

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Install Node.js dependencies:
```bash
npm install
```

### 3. Play via Web Interface

```bash
npm run dev
```
Open `http://localhost:3000` in your browser.

### 4. Play in Terminal (Pure Python CLI)

You can also play directly in your terminal without a browser:
```bash
python3 main.py
```

### 5. Run Python Unit Tests

Verify engine tactical strength and move generation speed:
```bash
python3 -m unittest discover -s tests
```

---

## How It Works

1. **Player Move**: When you move a piece on the board, legal moves are validated and the board updates instantly.
2. **Move Generation Pipeline**:
   - `backend/openings.py`: Checks grandmaster opening book for immediate response (< 5ms).
   - `backend/engine.py`: If outside the book, queries Stockfish calibrated to `UCI_LimitStrength: true` and `UCI_Elo: 2000` with an 180ms time budget.
   - `backend/search.py`: If external engine is unavailable, executes pure-Python iterative deepening alpha-beta search with MVV-LVA move ordering and Zobrist transposition table caching.
3. **Response**: Move is returned in standard JSON format and played on the board with highlighted origin and destination squares.

---

## Controls

- **Click piece**: Selects piece and highlights legal move destinations.
- **Click destination**: Executes the move.
- **MENU**:
  - `NEW GAME`: Resets board to starting position.
  - `FLIP BOARD`: Toggles orientation to play as Black or White.
  - `RESIGN`: Resigns current match.
- **UNDO / REDO**: Steps backward and forward through move history.

---

## License

This project is licensed under the [MIT License](LICENSE).
