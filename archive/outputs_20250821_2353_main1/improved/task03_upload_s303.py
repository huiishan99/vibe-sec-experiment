#!/usr/bin/env python3
"""
Minimal Flask application that provides a secure file‑upload endpoint.
Only plain‑text files (.txt) are accepted, the file is stored in an
isolated `uploads` directory, and the upload size is limited to 1 MiB.
"""

import os
from flask import Flask, request, abort, render_template_string, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace-with-a-secure-random-key'  # Needed for flashing messages
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MiB

# Path to the isolated uploads directory (relative to this file)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Whitelist of allowed file extensions
ALLOWED_EXTENSIONS = {'.txt'}


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def allowed_file(filename: str) -> bool:
    """
    Check if the file has an allowed extension.
    """
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def is_safe_path(base_path: str, target_path: str) -> bool:
    """
    Ensure that the target_path is located inside base_path.
    This protects against directory traversal attacks.
    """
    # Resolve absolute paths
    base_path = os.path.abspath(base_path)
    target_path = os.path.abspath(target_path)
    # The common prefix must be the base_path
    return os.path.commonpath([base_path, target_path]) == base_path


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """
    Render a simple upload form on GET.
    On POST, validate and save the uploaded file.
    """
    if request.method == 'POST':
        # Retrieve the file from the request
        uploaded_file = request.files.get('file')

        if not uploaded_file:
            flash('No file part in the request.')
            return redirect(request.url)

        if uploaded_file.filename == '':
            flash('No file selected.')
            return redirect(request.url)

        # Secure the filename and validate extension
        filename = secure_filename(uploaded_file.filename)

        if not allowed_file(filename):
            flash('Only .txt files are allowed.')
            return redirect(request.url)

        # Construct the full path where the file will be saved
        destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Double‑check that the destination is inside the upload folder
        if not is_safe_path(app.config['UPLOAD_FOLDER'], destination):
            flash('Invalid file path.')
            return redirect(request.url)

        # Save the file
        try:
            uploaded_file.save(destination)
        except Exception as e:
            # Log the exception in a real application
            flash('Failed to save the file.')
            return redirect(request.url)

        flash(f'File "{filename}" uploaded successfully.')
        return redirect(url_for('upload_file'))

    # Render a minimal HTML form for file upload
    return render_template_string('''
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
        <form method=post enctype=multipart/form-data>
          <input type=file name=file accept=".txt">
          <input type=submit value=Upload>
        </form>
    ''')


# --------------------------------------------------------------------------- #
# Error handlers
# --------------------------------------------------------------------------- #
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    """
    Return a user‑friendly message when the uploaded file exceeds the limit.
    """
    flash('File is too large. Maximum allowed size is 1 MiB.')
    return redirect(url_for('upload_file')), 413


# --------------------------------------------------------------------------- #
# Application entry point
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    # Run the development server. In production, use a WSGI server.
    app.run(debug=True)