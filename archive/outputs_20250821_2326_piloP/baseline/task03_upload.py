#!/usr/bin/env python3
"""
Minimal Flask application that provides a single route for uploading a file
and saving it to disk.

Author: Senior Python Engineer
"""

import os
from flask import Flask, request, redirect, url_for, render_template_string
from werkzeug.utils import secure_filename

# Configuration ---------------------------------------------------------------

# Directory where uploaded files will be stored
UPLOAD_FOLDER = "uploads"

# Optional: restrict allowed file extensions
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask application -----------------------------------------------------------

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max file size


def allowed_file(filename: str) -> bool:
    """
    Check if the file has an allowed extension.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes ---------------------------------------------------------------------

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    """
    Handle file upload via POST and display a simple upload form via GET.
    """
    if request.method == "POST":
        # Check if the post request has the file part
        if "file" not in request.files:
            return "No file part in the request", 400

        file = request.files["file"]

        # If user does not select a file, the browser may submit an empty part
        if file.filename == "":
            return "No selected file", 400

        if file and allowed_file(file.filename):
            # Secure the filename to prevent directory traversal attacks
            filename = secure_filename(file.filename)
            # Save the file to the upload folder
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            return f"File '{filename}' uploaded successfully!", 200

        return "File type not allowed", 400

    # GET request: show a simple upload form
    return render_template_string(
        """
        <!doctype html>
        <title>Upload File</title>
        <h1>Upload a file</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        """
    )


# Run the application ---------------------------------------------------------

if __name__ == "__main__":
    # Run in debug mode for development purposes
    app.run(debug=True)