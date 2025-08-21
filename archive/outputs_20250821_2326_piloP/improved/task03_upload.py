#!/usr/bin/env python3
"""
Minimal Flask application that provides a single route for uploading
plain‑text files (.txt).  The upload is protected against common
security pitfalls:

* Only files with a .txt extension are accepted.
* Filenames are sanitized with Werkzeug's `secure_filename` to
  eliminate path traversal characters.
* Uploaded files are stored in an isolated directory under the
  application root (`uploads/`).
* The maximum request size is limited to 1 MiB via
  `MAX_CONTENT_LENGTH`.
* The route returns clear error messages for invalid requests.
"""

from flask import Flask, request, abort, jsonify
from werkzeug.utils import secure_filename
import os

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# 1 MiB maximum upload size
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1,048,576 bytes

# Directory where uploads are stored (isolated from static/templates)
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"txt"}

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def is_allowed_file(filename: str) -> bool:
    """
    Return True if the file has an allowed extension.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handle file uploads.

    Expected form field: 'file'
    """
    # 1. Ensure a file part is present
    if "file" not in request.files:
        abort(400, description="Missing 'file' part in the request.")

    file = request.files["file"]

    # 2. Ensure a filename was provided
    if file.filename == "":
        abort(400, description="No file selected for uploading.")

    # 3. Sanitize the filename
    filename = secure_filename(file.filename)

    # 4. Verify the file extension
    if not is_allowed_file(filename):
        abort(400, description="Only .txt files are allowed.")

    # 5. Save the file to the isolated upload directory
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # The `secure_filename` call guarantees that `save_path` is safe
    # (no path traversal, no leading slashes, etc.)
    try:
        file.save(save_path)
    except Exception as exc:
        abort(500, description=f"Failed to save file: {exc}")

    return jsonify({"message": "File uploaded successfully", "filename": filename}), 201

# --------------------------------------------------------------------------- #
# Error handlers
# --------------------------------------------------------------------------- #

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle requests that exceed MAX_CONTENT_LENGTH."""
    return (
        jsonify({"error": "File is too large. Max size is 1 MB."}),
        413,
    )

@app.errorhandler(400)
def bad_request(error):
    """Return JSON for bad requests."""
    return jsonify({"error": error.description}), 400

@app.errorhandler(500)
def internal_error(error):
    """Return JSON for internal server errors."""
    return jsonify({"error": error.description}), 500

# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run the Flask development server (do not use in production)
    app.run(debug=True)