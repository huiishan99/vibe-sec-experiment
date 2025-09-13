#!/usr/bin/env python3
"""
Minimal Flask application that exposes a single route for uploading a file
and saving it to disk.

The route accepts a POST request with a multipart/form‑data body containing
a file field named "file".  The uploaded file is stored in the directory
specified by the UPLOAD_FOLDER configuration variable.

Author: Senior Python Engineer
"""

from flask import Flask, request, redirect, url_for, flash, render_template_string
from werkzeug.utils import secure_filename
import os

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
UPLOAD_FOLDER = "./uploads"          # Directory where uploaded files will be stored
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}  # Optional filter

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --------------------------------------------------------------------------- #
# Flask application setup
# --------------------------------------------------------------------------- #
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"  # Needed for flashing messages

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
@app.route("/", methods=["GET"])
def index():
    """
    Render a simple HTML form that allows the user to select a file for upload.
    """
    return render_template_string(
        """
        <!doctype html>
        <title>Upload a File</title>
        <h1>Upload a File</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul style="color: red;">
            {% for message in messages %}
              <li>{{ message }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <form method=post enctype=multipart/form-data action="{{ url_for('upload_file') }}">
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        """,
    )

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handle the file upload POST request.
    """
    # Check if the request has the file part
    if "file" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("index"))

    file = request.files["file"]

    # If no file was selected
    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    # Validate and secure the filename
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        try:
            file.save(save_path)
            flash(f"File successfully uploaded to {save_path}")
        except Exception as e:
            flash(f"Error saving file: {e}")
    else:
        flash("File type not allowed.")

    return redirect(url_for("index"))

# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Run in debug mode for development; remove or set debug=False in production
    app.run(debug=True)