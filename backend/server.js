const express = require("express");
const cors = require("cors");
const { execFile } = require("child_process");
const path = require("path");

const app = express();
app.use(cors());
app.use(express.json());

const PYTHON_SCRIPT = path.join(__dirname, "..", "rag_service.py");
const PROJECT_DIR = path.join(__dirname, "..");

app.post("/ask", (req, res) => {
  const { question } = req.body;

  if (!question || typeof question !== "string") {
    return res.status(400).json({ error: "question is required" });
  }

  execFile(
    "python",
    [PYTHON_SCRIPT, question],
    { cwd: PROJECT_DIR, maxBuffer: 1024 * 1024 * 10 },
    (error, stdout, stderr) => {
      if (error) {
        console.error(stderr);
        return res.status(500).json({ error: "Failed to generate answer" });
      }

      try {
        const result = JSON.parse(stdout);
        res.json(result);
      } catch (e) {
        console.error("Parse error:", stdout);
        res.status(500).json({ error: "Invalid response from RAG service" });
      }
    }
  );
});

app.get("/health", (req, res) => res.json({ status: "ok" }));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));