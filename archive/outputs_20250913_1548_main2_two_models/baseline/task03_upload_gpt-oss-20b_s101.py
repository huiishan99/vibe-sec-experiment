#!/usr/bin/env python3
"""
Minimal Flask application that exposes a single route for uploading a file
and saving it to disk.

Usage:
    1. Ensure Flask is installed: pip install Flask
    2. Run the app: python upload_app.py
    3. POST a file to http://127.0.0.1:5000/upload
"""

import os
from flask import Flask, request, abort, jsonify
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
UPLOAD_FOLDER = "uploads"          # Directory where uploaded files will be stored
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}  # Optional

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def allowed_file(filename: str) -> bool:
    """
    Check if the file has an allowed extension.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handle file upload via POST request.

    Expected form field: 'file'
    """
    # 1. Verify that the request contains a file part
    if "file" not in request.files:
        abort(400, description="No file part in the request")

    file = request.files["file"]

    # 2. If user does not select a file, the browser may submit an empty file
    if file.filename == "":
        abort(400, description="No selected file")

    # 3. Validate file extension (optional)
    if not allowed_file(file.filename):
        abort(400, description="File type not allowed")

    # 4. Secure the filename and save the file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # 5. Return a JSON response indicating success
    return jsonify({"message": "File uploaded successfully", "filename": filename}), 201


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Run the Flask development server
    app.run(debug=True)