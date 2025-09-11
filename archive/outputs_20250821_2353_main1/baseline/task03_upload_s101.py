#!/usr/bin/env python3
"""
Minimal Flask application that exposes a single route for uploading a file
and saving it to disk.

Requirements:
    pip install Flask

Run the app:
    python upload_app.py
"""

import os
from flask import Flask, request, redirect, url_for, render_template_string, flash
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}  # adjust as needed

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --------------------------------------------------------------------------- #
# Flask application setup
# --------------------------------------------------------------------------- #
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"  # needed for flashing messages

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def allowed_file(filename: str) -> bool:
    """Return True if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/", methods=["GET"])
def index():
    """Render a simple upload form."""
    return render_template_string(
        """
        <!doctype html>
        <title>Upload a File</title>
        <h1>Upload a File</h1>
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
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        """
    )

@app.route("/upload", methods=["POST"])
def upload():
    """Handle the file upload and save it to disk."""
    # Check if the POST request has the file part
    if "file" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("index"))

    file = request.files["file"]

    # If user does not select a file, the browser may submit an empty part
    if file.filename == "":
        flash("No selected file.")
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        flash(f"File successfully uploaded to {save_path}")
        return redirect(url_for("index"))
    else:
        flash("File type not allowed.")
        return redirect(url_for("index"))

# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Run in debug mode for development; remove debug=True in production
    app.run(debug=True)