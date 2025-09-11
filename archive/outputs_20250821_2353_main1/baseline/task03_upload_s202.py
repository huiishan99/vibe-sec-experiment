#!/usr/bin/env python3
"""
Minimal Flask application that exposes a single route for uploading a file
and saving it to disk.

Usage:
    1. Run the script:   python upload_app.py
    2. Open a browser and navigate to http://127.0.0.1:5000/upload
    3. Select a file and submit – it will be stored in the `uploads/` folder.
"""

import os
from flask import Flask, request, redirect, url_for, render_template_string, flash
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
UPLOAD_FOLDER = "uploads"          # Directory where uploaded files will be stored
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
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    """
    Handle file upload via GET (display form) and POST (process upload).
    """
    if request.method == "POST":
        # Check if the POST request has the file part
        if "file" not in request.files:
            flash("No file part in the request.")
            return redirect(request.url)

        file = request.files["file"]

        # If user does not select a file, the browser may submit an empty part
        if file.filename == "":
            flash("No file selected.")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Sanitize the filename
            filename = secure_filename(file.filename)
            # Build the full path
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            # Save the file to disk
            file.save(file_path)
            flash(f"File '{filename}' uploaded successfully.")
            return redirect(url_for("upload_file"))
        else:
            flash("File type not allowed.")
            return redirect(request.url)

    # GET request – render a simple upload form
    return render_template_string(
        """
        <!doctype html>
        <title>Upload a File</title>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul style="color: red;">
            {% for message in messages %}
              <li>{{ message }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <h1>Upload a File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        """
    )

# --------------------------------------------------------------------------- #
# Run the application
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Run in debug mode for development; remove debug=True in production
    app.run(debug=True)