#!/usr/bin/env python3
"""
Minimal Flask application that securely handles file uploads.

Features:
- Only accepts files with a .txt extension.
- Uses werkzeug.utils.secure_filename to sanitize filenames.
- Rejects absolute paths and any attempt to traverse directories (e.g. '..').
- Stores uploads in an isolated directory (`uploads/`).
- Limits upload size to 1 MiB (MAX_CONTENT_LENGTH).
"""

import os
from flask import Flask, request, redirect, url_for, flash, render_template_string
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
ALLOWED_EXTENSIONS = {".txt"}
MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MiB

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.secret_key = "replace-with-a-secure-random-key"  # Needed for flash messages

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def is_allowed_file(filename: str) -> bool:
    """
    Check if the file has an allowed extension.
    """
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS

def is_safe_path(base: str, path: str) -> bool:
    """
    Ensure that the resolved absolute path is within the base directory.
    This protects against directory traversal attacks.
    """
    # Resolve the absolute path
    resolved = os.path.abspath(os.path.join(base, path))
    # The resolved path must start with the base directory
    return resolved.startswith(base)

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
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul style="color: red;">
            {% for msg in messages %}
              <li>{{ msg }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <h1>Upload a .txt file</h1>
        <form method=post enctype=multipart/form-data action="{{ url_for('upload') }}">
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        """
    )

@app.route("/upload", methods=["POST"])
def upload():
    """
    Handle the file upload.
    """
    if "file" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    # Sanitize the filename
    filename = secure_filename(file.filename)

    # Reject if the filename is empty after sanitization
    if not filename:
        flash("Invalid file name.")
        return redirect(url_for("index"))

    # Enforce allowed extensions
    if not is_allowed_file(filename):
        flash("Only .txt files are allowed.")
        return redirect(url_for("index"))

    # Prevent directory traversal by ensuring the filename does not contain '..'
    if ".." in filename or os.path.isabs(filename):
        flash("Invalid file path.")
        return redirect(url_for("index"))

    # Build the full path and ensure it stays within the upload folder
    target_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not is_safe_path(app.config["UPLOAD_FOLDER"], target_path):
        flash("Attempted directory traversal detected.")
        return redirect(url_for("index"))

    # Save the file
    try:
        file.save(target_path)
    except Exception as e:
        flash(f"Failed to save file: {e}")
        return redirect(url_for("index"))

    flash(f"File '{filename}' uploaded successfully.")
    return redirect(url_for("index"))

# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # In production, use a proper WSGI server instead of Flask's built‑in server.
    app.run(debug=True)