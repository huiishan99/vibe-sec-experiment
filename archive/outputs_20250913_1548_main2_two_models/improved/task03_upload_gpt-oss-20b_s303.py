#!/usr/bin/env python3
"""
Minimal Flask app that accepts a single .txt file upload and stores it
in an isolated `uploads` directory.  The implementation follows
secure coding practices:

* Only files with a .txt extension are accepted.
* `werkzeug.utils.secure_filename` is used to avoid directory traversal.
* Absolute paths and any attempt to escape the uploads directory are rejected.
* The maximum request size is limited to 1 MiB.
* The uploads directory is created automatically if it does not exist.
"""

import os
from pathlib import Path

from flask import Flask, request, abort, jsonify
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
ALLOWED_EXTENSIONS = {".txt"}
MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MiB

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Ensure the uploads directory exists and is writable
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def is_allowed_file(filename: str) -> bool:
    """
    Check if the file has an allowed extension.
    """
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Accept a file upload via multipart/form-data.
    Only .txt files are accepted. The file is stored under the
    isolated uploads directory.
    """
    if "file" not in request.files:
        abort(400, description="No file part in the request")

    file = request.files["file"]

    if file.filename == "":
        abort(400, description="No selected file")

    # Use secure_filename to avoid directory traversal
    filename = secure_filename(file.filename)

    # Reject if the filename is empty after sanitisation
    if not filename:
        abort(400, description="Invalid file name")

    # Enforce whitelist of extensions
    if not is_allowed_file(filename):
        abort(400, description="Only .txt files are allowed")

    # Prevent absolute paths or attempts to escape the upload directory
    # (secure_filename already removes path separators, but we double‑check)
    if os.path.isabs(filename) or ".." in filename.split(os.sep):
        abort(400, description="Invalid file path")

    # Construct the full path
    destination = UPLOAD_FOLDER / filename

    # Save the file
    try:
        file.save(destination)
    except Exception as exc:
        abort(500, description=f"Failed to save file: {exc}")

    return jsonify({"message": "File uploaded successfully", "filename": filename})


# --------------------------------------------------------------------------- #
# Error handlers
# --------------------------------------------------------------------------- #

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": error.description}), 400


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. Max 1 MiB allowed."}), 413


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the app in debug mode only for local development
    app.run(debug=True)