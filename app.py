from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime
from file_utils import extract_text
from summarizer import generate_summary

# Securely bind the Gemini Cloud API credentials from the .env environment matrix
load_dotenv()

app = Flask(__name__)
# Security: Hard limit total upload payload to 25MB to prevent physical server RAM explosion crashes
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

UPLOAD_FOLDER = "uploads"
DB_FILE = "history.db"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Generate database schema if it doesn't dynamically exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            summary TEXT,
            word_count INTEGER,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Architecture fix: Safely encode filename to prevent Hackers passing path traversal bugs (e.g. ../../../app.py)
    safe_filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    file.save(file_path)

    try:
        text = extract_text(file_path)
        if not text.strip():
            return jsonify({"error": "Could not extract text from file"}), 400

        summary = generate_summary(text)

        # Automatically save generated log into persistent history.db
        word_count = len(summary.split())
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # Log date format: "YYYY-MM-DD HH:MM"
        c.execute("INSERT INTO summaries (filename, summary, word_count, created_at) VALUES (?, ?, ?, ?)",
                  (safe_filename, summary, word_count, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()

        return jsonify({"summary": summary})
    finally:
        # Architecture fix: Force self-clean destruct of file after reading to stop extreme Hard-Drive storage bloat
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route("/history", methods=["GET"])
def get_history():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, filename, summary, word_count, created_at FROM summaries ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    
    # Return JSON representation of database logs
    return jsonify({"history": [dict(row) for row in rows]})

@app.route("/history/<int:summary_id>", methods=["DELETE"])
def delete_history(summary_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)