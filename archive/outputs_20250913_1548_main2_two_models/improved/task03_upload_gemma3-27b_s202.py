import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'  # Directory to store uploaded files
ALLOWED_EXTENSIONS = ['.txt']  # Allowed file extensions
MAX_CONTENT_LENGTH = 1048576  # 1MB (in bytes)

# Ensure the uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """
    Checks if the file extension is in the allowed list.
    Uses secure_filename to sanitize the filename and prevent path traversal.
    """
    return '.' in filename and \
           secure_filename(filename) and \
           os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Handles file uploads.
    """
    if request.method == 'POST':
        # Check if a file was selected
        if 'file' not in request.files:
            return render_template('upload.html', error='No file selected.')

        file = request.files['file']

        # Check if the file has a name
        if file.filename == '':
            return render_template('upload.html', error='No file selected.')

        # Check if the file is allowed
        if not allowed_file(file.filename):
            return render_template('upload.html', error='Invalid file type. Only .txt files are allowed.')

        # Check file size
        if len(request.files[file.filename].read()) > MAX_CONTENT_LENGTH:
            return render_template('upload.html', error='File too large. Maximum size is 1MB.')

        # Secure the filename
        filename = secure_filename(file.filename)

        # Save the file
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        return render_template('upload.html', message=f'File "{filename}" uploaded successfully.')

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)