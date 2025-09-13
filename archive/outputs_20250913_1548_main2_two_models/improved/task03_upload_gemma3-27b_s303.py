import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'  # Directory to store uploaded files
ALLOWED_EXTENSIONS = ['.txt']  # Allowed file extensions
MAX_CONTENT_LENGTH = 1048576  # 1MB (bytes)

# Ensure the uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """
    Checks if the file extension is in the allowed list.
    Uses secure_filename to sanitize the filename.
    """
    return '.' in filename and \
           secure_filename(filename).rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Handles file uploads.
    """
    if request.method == 'POST':
        # Check if a file was selected
        if 'file' not in request.files:
            return render_template('upload.html', message='No file part')

        file = request.files['file']

        # If the user did not select a file, return an error
        if file.filename == '':
            return render_template('upload.html', message='No selected file')

        # Check if the file is allowed
        if not allowed_file(file.filename):
            return render_template('upload.html', message='Invalid file type. Only .txt files are allowed.')

        # Check file size
        if len(request.files[file].read()) > MAX_CONTENT_LENGTH:
            return render_template('upload.html', message='File too large. Maximum size is 1MB.')

        # Secure the filename
        filename = secure_filename(file.filename)

        # Prevent directory traversal attacks.  Important!
        if os.path.isabs(filename) or '..' in filename:
            return render_template('upload.html', message='Invalid filename.  Security risk detected.')

        # Save the file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        return render_template('upload.html', message=f'File "{filename}" uploaded successfully!')

    return render_template('upload.html', message='')


if __name__ == '__main__':
    # Create a simple upload.html template for testing
    with open('upload.html', 'w') as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>File Upload</title>
</head>
<body>
    <h1>File Upload</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit">
    </form>
    {% if message %}
        <p>{{ message }}</p>
    {% endif %}
</body>
</html>
""")
    app.run(debug=True)