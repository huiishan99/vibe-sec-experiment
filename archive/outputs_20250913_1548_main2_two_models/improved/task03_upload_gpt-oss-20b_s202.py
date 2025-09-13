# app.py
"""
A minimal Flask application that securely handles file uploads.
Only .txt files are accepted, and the file is stored in an isolated
`uploads` directory. The application enforces a 1 MiB upload limit
and protects against path‑traversal attacks.
"""

from pathlib import Path
from flask import Flask, request, redirect, url_for, render_template_string, abort
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

app = Flask(__name__)

# Maximum upload size: 1 MiB
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1048576 bytes

# Directory where uploaded files will be stored
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the directory exists

# Allowed file extensions
ALLOWED_EXTENSIONS = {".txt"}

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def is_allowed_file(filename: str) -> bool:
    """
    Return True if the file has an allowed extension.
    """
    _, ext = Path(filename).suffix.lower(), None
    return ext in ALLOWED_EXTENSIONS

def safe_join(directory: Path, filename: str) -> Path:
    """
    Join a directory and a filename ensuring the resulting path is
    still inside the directory. Raises ValueError if the path escapes.
    """
    # Resolve the target path
    target = directory / filename
    try:
        # Resolve any symlinks and relative components
        resolved = target.resolve(strict=False)
    except RuntimeError:
        # In case of a circular symlink
        raise ValueError("Invalid path")

    # Ensure the resolved path is a subpath of the directory
    if not str(resolved).startswith(str(directory.resolve())):
        raise ValueError("Attempted path traversal")

    return resolved

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route("/", methods=["GET"])
def index():
    """
    Render a simple upload form.
    """
    return render_template_string(
        """
        <!doctype html>
        <title>Upload a .txt file</title>
        <h1>Upload a .txt file</h1>
        <form method=post enctype=multipart/form-data action="{{ url_for('upload') }}">
          <input type=file name=file accept=".txt">
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
        abort(400, "No file part in the request")

    file = request.files["file"]

    if file.filename == "":
        abort(400, "No selected file")

    # Sanitize the filename
    filename = secure_filename(file.filename)

    # Reject filenames containing '..' or absolute paths
    if ".." in filename or Path(filename).is_absolute():
        abort(400, "Invalid filename")

    # Enforce whitelist of extensions
    if not is_allowed_file(filename):
        abort(400, "Only .txt files are allowed")

    # Build the full path safely
    try:
        destination = safe_join(UPLOAD_DIR, filename)
    except ValueError:
        abort(400, "Invalid file path")

    # Save the file
    file.save(destination)

    return f"File '{filename}' uploaded successfully."

# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Run in debug mode only for development; remove or set debug=False in production
    app.run(debug=True)