/**
 * Dave Christopher Chess Engine — Frontend Interface Controller
 */

const game = new Chess();
const boardEl = document.getElementById('board');
const gameOverEl = document.getElementById('game-over-status');
const settingsMenu = document.getElementById('settings-menu');

let selectedSquare = null;
let legalMoves = [];
let lastMove = null;
let gameActive = true;
let historyStack = [];
let playerColor = 'w';
let isThinking = false;

const pieceUrl = (piece) => {
    const type = piece.type.toUpperCase();
    const color = piece.color;
    const pieceMap = {
        'WK': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Chess_klt45.svg',
        'WQ': 'https://upload.wikimedia.org/wikipedia/commons/1/15/Chess_qlt45.svg',
        'WR': 'https://upload.wikimedia.org/wikipedia/commons/7/72/Chess_rlt45.svg',
        'WB': 'https://upload.wikimedia.org/wikipedia/commons/b/b1/Chess_blt45.svg',
        'WN': 'https://upload.wikimedia.org/wikipedia/commons/7/70/Chess_nlt45.svg',
        'WP': 'https://upload.wikimedia.org/wikipedia/commons/4/45/Chess_plt45.svg',
        'BK': 'https://upload.wikimedia.org/wikipedia/commons/f/f0/Chess_kdt45.svg',
        'BQ': 'https://upload.wikimedia.org/wikipedia/commons/4/47/Chess_qdt45.svg',
        'BR': 'https://upload.wikimedia.org/wikipedia/commons/f/ff/Chess_rdt45.svg',
        'BB': 'https://upload.wikimedia.org/wikipedia/commons/9/98/Chess_bdt45.svg',
        'BN': 'https://upload.wikimedia.org/wikipedia/commons/e/ef/Chess_ndt45.svg',
        'BP': 'https://upload.wikimedia.org/wikipedia/commons/c/c7/Chess_pdt45.svg'
    };
    return pieceMap[`${color.toUpperCase()}${type}`];
};

async function makeBotMove() {
    if (!gameActive || game.game_over() || isThinking) return;
    isThinking = true;

    try {
        const moves = game.moves({ verbose: true });
        if (moves.length === 0) {
            isThinking = false;
            return;
        }

        const payloadMoves = moves.map(m => {
            game.move(m);
            const fen = game.fen();
            game.undo();
            return {
                from: m.from,
                to: m.to,
                promotion: m.promotion,
                captured: m.captured,
                fen: fen,
                san: m.san
            };
        });

        const response = await fetch('/api/bot-move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                moves: payloadMoves,
                botColor: playerColor === 'w' ? 'b' : 'w',
                fen: game.fen()
            })
        });

        const bestMoveData = await response.json();
        if (bestMoveData && bestMoveData.from && bestMoveData.to) {
            const moveResult = game.move({
                from: bestMoveData.from,
                to: bestMoveData.to,
                promotion: bestMoveData.promotion || 'q'
            });
            if (moveResult) {
                lastMove = { from: moveResult.from, to: moveResult.to };
            }
        } else if (moves.length > 0) {
            const fallback = moves[Math.floor(Math.random() * moves.length)];
            const moveResult = game.move(fallback);
            if (moveResult) {
                lastMove = { from: moveResult.from, to: moveResult.to };
            }
        }
    } catch (err) {
        console.error('Bot move error:', err);
        const moves = game.moves({ verbose: true });
        if (moves.length > 0) {
            const fallback = moves[Math.floor(Math.random() * moves.length)];
            const moveResult = game.move(fallback);
            if (moveResult) {
                lastMove = { from: moveResult.from, to: moveResult.to };
            }
        }
    } finally {
        isThinking = false;
        renderBoard();
    }
}

function undoMove() {
    if (game.history().length >= 2 && gameActive && !isThinking) {
        let botM = game.undo();
        let playerM = game.undo();
        historyStack.push([playerM, botM]);
        lastMove = null;
        renderBoard();
    }
}

function redoMove() {
    if (historyStack.length > 0 && gameActive && !isThinking) {
        let moves = historyStack.pop();
        game.move(moves[0]);
        const m = game.move(moves[1]);
        lastMove = { from: m.from, to: m.to };
        renderBoard();
    }
}

function renderBoard() {
    boardEl.innerHTML = '';
    const boardState = game.board();
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const r = playerColor === 'w' ? row : 7 - row;
            const c = playerColor === 'w' ? col : 7 - col;

            const squareId = String.fromCharCode(97 + c) + (8 - r);
            const piece = boardState[r][c];
            const squareDiv = document.createElement('div');
            squareDiv.className = `square ${(r + c) % 2 === 0 ? 'light' : 'dark'}`;
            squareDiv.id = squareId;
            
            if (col === 0) {
                const rank = document.createElement('div');
                rank.className = 'coord coord-rank';
                rank.innerText = 8 - r;
                squareDiv.appendChild(rank);
            }
            if (row === 7) {
                const file = document.createElement('div');
                file.className = 'coord coord-file';
                file.innerText = String.fromCharCode(97 + c);
                squareDiv.appendChild(file);
            }
            
            if (selectedSquare === squareId || (lastMove && (lastMove.from === squareId || lastMove.to === squareId))) {
                const hl = document.createElement('div');
                hl.className = 'highlight';
                squareDiv.appendChild(hl);
            }
            
            if (piece) {
                const pDiv = document.createElement('div');
                pDiv.className = 'piece';
                pDiv.style.backgroundImage = `url(${pieceUrl(piece)})`;
                squareDiv.appendChild(pDiv);
            }
            
            const moveHint = legalMoves.find(m => m.to === squareId);
            if (moveHint) {
                const hintDiv = document.createElement('div');
                hintDiv.className = moveHint.flags.includes('c') ? 'hint-capture' : 'hint-dot';
                squareDiv.appendChild(hintDiv);
            }
            
            squareDiv.onclick = () => onSquareClick(squareId);
            boardEl.appendChild(squareDiv);
        }
    }
    checkGameOver();
}

function onSquareClick(sq) {
    if (!gameActive || game.turn() !== playerColor || isThinking) return;
    
    if (selectedSquare) {
        const move = game.move({ from: selectedSquare, to: sq, promotion: 'q' });
        if (move) {
            lastMove = { from: move.from, to: move.to };
            selectedSquare = null;
            legalMoves = [];
            historyStack = []; 
            renderBoard();
            if (!game.game_over()) {
                makeBotMove();
            }
        } else {
            const pieceOnClicked = game.get(sq);
            if (pieceOnClicked && pieceOnClicked.color === playerColor) {
                selectedSquare = sq;
                legalMoves = game.moves({ square: sq, verbose: true });
            } else {
                selectedSquare = null;
                legalMoves = [];
            }
            renderBoard();
        }
    } else {
        const piece = game.get(sq);
        if (piece && piece.color === playerColor) {
            selectedSquare = sq;
            legalMoves = game.moves({ square: sq, verbose: true });
            renderBoard();
        }
    }
}

function checkGameOver() {
    if (!gameActive) return; 
    if (game.in_checkmate()) {
        gameOverEl.innerText = game.turn() === playerColor ? '0-1 • DAVE WON' : '1-0 • YOU WON';
        gameOverEl.style.display = 'block';
        gameActive = false;
    } else if (game.in_draw()) {
        gameOverEl.innerText = '1/2-1/2 • DRAW';
        gameOverEl.style.display = 'block';
        gameActive = false;
    }
}

function toggleSettings() {
    settingsMenu.classList.toggle('show');
}

function handleMenu(action) {
    settingsMenu.classList.remove('show');
    if (action === 'new') {
        game.reset();
        gameActive = true;
        lastMove = null;
        historyStack = [];
        gameOverEl.innerText = '';
        gameOverEl.style.display = 'none';
        if (playerColor === 'b') {
            makeBotMove();
        }
    } else if (action === 'flip') {
        playerColor = playerColor === 'w' ? 'b' : 'w';
        selectedSquare = null;
        legalMoves = [];
        renderBoard();
        if (gameActive && game.turn() !== playerColor) {
            makeBotMove();
        }
    } else if (action === 'resign' && gameActive) {
        gameActive = false;
        gameOverEl.innerText = '0-1 • YOU RESIGNED';
        gameOverEl.style.display = 'block';
    }
    selectedSquare = null;
    legalMoves = [];
    renderBoard();
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('.top-controls')) {
        settingsMenu.classList.remove('show');
    }
});

// Ambient particle canvas effect
(function initRain() {
    const canvas = document.getElementById('rainCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let drops = [];
    let dpr = Math.min(window.devicePixelRatio || 1, 2);

    function resize() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = window.innerWidth * dpr;
        canvas.height = window.innerHeight * dpr;
        canvas.style.width = window.innerWidth + 'px';
        canvas.style.height = window.innerHeight + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        const area = window.innerWidth * window.innerHeight;
        const count = Math.min(140, Math.max(35, Math.floor(area / 11000)));
        drops = Array.from({ length: count }, makeDrop);
    }

    function makeDrop() {
        return {
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            len: 5 + Math.random() * 7,
            speed: 1.4 + Math.random() * 1.6,
            drift: 0.15 + Math.random() * 0.15,
            alpha: 0.12 + Math.random() * 0.22
        };
    }

    function step() {
        ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        for (const d of drops) {
            ctx.globalAlpha = d.alpha;
            ctx.beginPath();
            ctx.moveTo(Math.round(d.x), Math.round(d.y));
            ctx.lineTo(Math.round(d.x - d.drift * d.len), Math.round(d.y + d.len));
            ctx.stroke();

            d.y += d.speed;
            d.x -= d.drift;

            if (d.y > window.innerHeight + d.len) {
                d.y = -d.len;
                d.x = Math.random() * window.innerWidth;
            }
            if (d.x < -20) d.x = window.innerWidth + 20;
        }
        ctx.globalAlpha = 1;
        requestAnimationFrame(step);
    }

    window.addEventListener('resize', resize);
    resize();
    requestAnimationFrame(step);
    requestAnimationFrame(() => canvas.classList.add('rain-visible'));
})();

// Expose handlers to global window for HTML inline events
window.toggleSettings = toggleSettings;
window.handleMenu = handleMenu;
window.undoMove = undoMove;
window.redoMove = redoMove;

renderBoard();
if (playerColor === 'b' && game.turn() === 'b') {
    makeBotMove();
}
