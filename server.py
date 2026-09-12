#!/usr/bin/env python3
"""
Dave Christopher Chess Engine — Standalone Python Web & API Server
Serves the retro frontend interface and provides the 2000 ELO chess engine REST API.
Can be launched independently with: python3 backend/server.py
"""

import http.server
import socketserver
import json
import os
import sys
import mimetypes

# Ensure backend root is accessible
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
sys.path.insert(0, BACKEND_DIR)

from engine import select_best_move

PORT = int(os.environ.get("PYTHON_PORT", 8080))


class ChessHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler for Dave Christopher Chess Engine."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            payload = json.dumps({"status": "ok", "engine": "davechristopher", "elo": 2000})
            self.wfile.write(payload.encode("utf-8"))
            return

        if self.path in ("/", "/index.html"):
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/bot-move":
            content_length = int(self.headers.get("Content-Length", 0))
            body_raw = self.rfile.read(content_length).decode("utf-8")
            try:
                body = json.loads(body_raw)
                fen = body.get("fen", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
                elo = int(body.get("elo", 2000))
                time_limit = float(body.get("timeLimit", 0.18))

                move_data = select_best_move(fen=fen, target_elo=elo, time_limit=time_limit)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(move_data or {}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def end_headers(self):
        # Enable CORS for local development
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()


def run_server(port: int = PORT):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", port), ChessHandler) as httpd:
        print(f"Dave Christopher Python Server running at http://0.0.0.0:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.shutdown()


if __name__ == "__main__":
    run_server()
