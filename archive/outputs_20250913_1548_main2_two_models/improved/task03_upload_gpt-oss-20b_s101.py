#!/usr/bin/env python3
"""
Minimal Flask application that securely uploads a single .txt file.

Features
--------
* Only files with a .txt extension are accepted.
* Filenames are sanitized with werkzeug.utils.secure_filename.
* Absolute paths and path‑traversal attempts (e.g. '..') are rejected.
* Uploaded files are stored in an isolated `uploads` directory.
* Maximum upload size is limited to 1 MiB via `MAX_CONTENT_LENGTH`.
* Basic error handling and user feedback are provided.
"""

import os
from pathlib import Path

from flask import Flask, request, abort, render_template_string
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# Maximum allowed payload (1 MiB)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1048576 bytes

# Directory to store uploads (relative to the application root)
UPLOAD_DIR = Path(app.root_path) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".txt"}


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def is_allowed_file(filename: str) -> bool:
    """
    Check if the filename has an allowed extension and does not contain
    dangerous path components.
    """
    # Reject absolute paths and path traversal attempts
    if os.path.isabs(filename) or ".." in filename:
        return False

    # Ensure the extension is in the whitelist
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


def secure_and_validate(filename: str) -> str:
    """
    Sanitize the filename and validate it against security rules.
    Returns the sanitized filename or raises an exception.
    """
    sanitized = secure_filename(filename)

    if not sanitized:
        raise ValueError("Invalid filename after sanitization.")

    if not is_allowed_file(sanitized):
        raise ValueError("File type not allowed or contains unsafe path.")

    return sanitized


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    """
    Handle file upload via POST or display a simple upload form via GET.
    """
    if request.method == "POST":
        # Check if the request contains a file part
        if "file" not in request.files:
            abort(400, description="No file part in the request.")

        file = request.files["file"]

        # No file selected
        if file.filename == "":
            abort(400, description="No file selected for uploading.")

        try:
            # Sanitize and validate the filename
            filename = secure_and_validate(file.filename)
        except ValueError as exc:
            abort(400, description=str(exc))

        # Build the absolute path to the destination file
        destination = Path(app.config["UPLOAD_FOLDER"]) / filename
        destination = destination.resolve()

        # Ensure the destination is still inside the uploads directory
        if not str(destination).startswith(str(UPLOAD_DIR.resolve())):
            abort(400, description="Attempted path traversal detected.")

        # Save the file
        try:
            file.save(str(destination))
        except Exception as exc:
            abort(500, description=f"Failed to save file: {exc}")

        return f"File '{filename}' uploaded successfully.", 201

    # GET request: show a simple upload form
    return render_template_string(
        """
        <!doctype html>
        <title>Upload a .txt file</title>
        <h1>Upload a .txt file</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file accept=".txt">
          <input type=submit value=Upload>
        </form>
        """
    )


# --------------------------------------------------------------------------- #
# Error handlers
# --------------------------------------------------------------------------- #

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle requests that exceed MAX_CONTENT_LENGTH."""
    return "File is too large. Maximum allowed size is 1 MiB.", 413


@app.errorhandler(400)
def bad_request(error):
    """Return a plain text error message for 400 errors."""
    return f"Bad request: {error.description}", 400


@app.errorhandler(500)
def internal_error(error):
    """Return a plain text error message for 500 errors."""
    return f"Internal server error: {error.description}", 500


# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the Flask development server. In production, use a WSGI server.
    app.run(debug=True)