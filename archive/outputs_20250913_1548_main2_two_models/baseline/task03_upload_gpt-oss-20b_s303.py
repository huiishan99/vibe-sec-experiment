# app.py
"""
Minimal Flask application that provides a single route for uploading a file
and saving it to disk.

Usage:
    python app.py
    Open http://127.0.0.1:5000/upload in a browser.
"""

import os
from pathlib import Path
from flask import Flask, request, redirect, url_for, render_template_string
from werkzeug.utils import secure_filename

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

# Ensure the upload folder exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)


def allowed_file(filename: str) -> bool:
    """Return True if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Simple HTML form for uploading files
UPLOAD_FORM = """
<!doctype html>
<title>Upload a File</title>
<h1>Upload a File</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
{% if message %}
<p><strong>{{ message }}</strong></p>
{% endif %}
"""


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    """
    Handle file upload:
    - GET: show upload form.
    - POST: validate and save the uploaded file.
    """
    if request.method == "POST":
        # Check if the post request has the file part
        if "file" not in request.files:
            return render_template_string(UPLOAD_FORM, message="No file part")
        file = request.files["file"]
        # If user does not select file, browser may submit an empty part
        if file.filename == "":
            return render_template_string(UPLOAD_FORM, message="No selected file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = app.config["UPLOAD_FOLDER"] / filename
            file.save(save_path)
            return render_template_string(
                UPLOAD_FORM, message=f"File '{filename}' uploaded successfully."
            )
        else:
            return render_template_string(
                UPLOAD_FORM, message="File type not allowed"
            )
    # GET request
    return render_template_string(UPLOAD_FORM)


if __name__ == "__main__":
    # Run the Flask development server
    app.run(debug=True)