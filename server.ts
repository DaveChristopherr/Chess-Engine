import express from "express";
import path from "path";
import { spawn } from "child_process";
import { createServer as createViteServer } from "vite";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Dave Christopher 2000 ELO Engine API
  app.post("/api/bot-move", (req, res) => {
    const scriptPath = path.join(process.cwd(), "backend", "engine.py");
    const pythonProcess = spawn("python3", [scriptPath]);

    let outputData = "";
    let errorData = "";

    pythonProcess.stdout.on("data", (data) => {
      outputData += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      errorData += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0 && errorData) {
        console.error("Engine process error:", errorData);
      }
      try {
        const result = JSON.parse(outputData.trim());
        res.json(result);
      } catch (err) {
        console.error("Failed to parse engine output:", outputData, err);
        const moves = req.body.moves || [];
        res.json(moves[0] || null);
      }
    });

    pythonProcess.on("error", (err) => {
      console.error("Failed to spawn engine:", err);
      const moves = req.body.moves || [];
      res.json(moves[0] || null);
    });

    const payload = {
      fen: req.body.fen,
      elo: 2000,
      timeLimit: 0.18,
      moves: req.body.moves || []
    };

    pythonProcess.stdin.write(JSON.stringify(payload));
    pythonProcess.stdin.end();
  });

  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", engine: "davechristopher", elo: 2000 });
  });

  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "mpa",
    });
    app.use(vite.middlewares);

    app.get("/", (req, res) => {
      res.sendFile(path.join(process.cwd(), "index.html"));
    });
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*all", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Dave Christopher Chess Engine running on http://localhost:${PORT}`);
  });
}

startServer();
