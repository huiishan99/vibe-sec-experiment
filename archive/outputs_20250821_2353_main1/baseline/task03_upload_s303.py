# app.py
"""
A minimal Flask application that exposes a single route for uploading a file
and saving it to disk.

Requirements:
    pip install flask

Usage:
    1. Run the app:
        python app.py
    2. Open http://127.0.0.1:5000/ in a browser.
    3. Use the form to upload a file. The file will be stored in the
       `uploads/` directory relative to this script.
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
app.secret_key = "supersecretkey"  # required for flashing messages

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
    Render a simple upload form.
    """
    return render_template_string(
        """
        <!doctype html>
        <title>Upload File</title>
        <h1>Upload a file</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul style="color: red;">
            {% for msg in messages %}
              <li>{{ msg }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <form method=post enctype=multipart/form-data action="{{ url_for('upload_file') }}">
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        """
    )

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handle the file upload and save it to disk.
    """
    # Check if the request contains a file part
    if "file" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("index"))

    file = request.files["file"]

    # If no file is selected, the browser may submit an empty file
    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        # Sanitize the filename
        filename = secure_filename(file.filename)
        # Build the full path
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        # Save the file
        file.save(file_path)
        flash(f"File '{filename}' uploaded successfully.")
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