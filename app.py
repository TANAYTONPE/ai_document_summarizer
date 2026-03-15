from flask import Flask, request, jsonify
import os
from file_utils import extract_text
from summarizer import generate_summary
from flask import render_template
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/summarize", methods=["POST"])
def summarize():

    file = request.files["file"]
    if file is None or file.filename == "":
        return jsonify({"error": "No file uploaded"})
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    text = extract_text(file_path)

    if not text:
        return jsonify({"error": "No text found"})

    summary = generate_summary(text)

    return jsonify({
        "summary": summary
    })

if __name__ == "__main__":
    app.run(debug=True)