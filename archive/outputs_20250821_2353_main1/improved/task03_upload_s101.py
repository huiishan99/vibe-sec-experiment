#!/usr/bin/env python3
"""
Minimal Flask application that securely accepts a single .txt file upload.

Features
--------
* Only files with a .txt extension are allowed.
* Filenames are sanitized with werkzeug.utils.secure_filename.
* Absolute paths and directory traversal attempts (e.g. '..') are rejected.
* Uploaded files are stored in an isolated `uploads` directory.
* The maximum allowed upload size is 1 MiB (1048576 bytes).
"""

import os
from pathlib import Path

from flask import (
    Flask,
    request,
    abort,
    render_template_string,
    redirect,
    url_for,
    flash,
)
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Directory where uploads will be stored. It is created on startup if missing.
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Allowed file extensions (whitelist)
ALLOWED_EXTENSIONS = {".txt"}

# Flask configuration
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 1_048_576  # 1 MiB
app.secret_key = "replace-with-a-secure-random-key"  # Needed for flash messages

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def is_allowed_file(filename: str) -> bool:
    """
    Return True if the file has an allowed extension.
    """
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def is_safe_path(path: str) -> bool:
    """
    Reject absolute paths and any attempt to traverse directories.
    """
    # Reject absolute paths
    if os.path.isabs(path):
        return False
    # Reject paths containing '..'
    if ".." in Path(path).parts:
        return False
    return True


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route("/", methods=["GET"])
def index():
    """
    Simple upload form.
    """
    return render_template_string(
        """
        <!doctype html>
        <title>Upload a .txt file</title>
        <h1>Upload a .txt file</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul style="color: red;">
            {% for msg in messages %}
              <li>{{ msg }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <form method=post enctype=multipart/form-data action="{{ url_for('upload') }}">
          <input type=file name=file accept=".txt">
          <input type=submit value=Upload>
        </form>
        """,
    )


@app.route("/upload", methods=["POST"])
def upload():
    """
    Handle file upload.
    """
    if "file" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    # Sanitize filename
    filename = secure_filename(file.filename)

    # Reject unsafe filenames
    if not is_safe_path(filename):
        flash("Invalid filename.")
        return redirect(url_for("index"))

    # Enforce whitelist
    if not is_allowed_file(filename):
        flash("Only .txt files are allowed.")
        return redirect(url_for("index"))

    # Save the file
    destination = app.config["UPLOAD_FOLDER"] / filename
    try:
        file.save(destination)
    except Exception as exc:
        # Log the exception in a real application
        flash(f"Failed to save file: {exc}")
        return redirect(url_for("index"))

    flash(f"File '{filename}' uploaded successfully.")
    return redirect(url_for("index"))


# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # In production, use a proper WSGI server instead of Flask's built‑in server.
    app.run(debug=True)