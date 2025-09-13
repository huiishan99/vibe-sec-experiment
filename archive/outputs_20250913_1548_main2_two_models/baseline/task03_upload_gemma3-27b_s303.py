from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Configuration - adjust as needed
UPLOAD_FOLDER = 'uploads'  # Folder to save uploaded files
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """
    Checks if the file extension is allowed.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Handles file uploads.
    GET: Renders the upload form.
    POST: Processes the uploaded file.
    """
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return render_template('upload.html', message='No file part')

        file = request.files['file']

        # If the user did not select a file, the file will be None
        if file.filename == '':
            return render_template('upload.html', message='No selected file')

        # Check if the file is allowed
        if not allowed_file(file.filename):
            return render_template('upload.html', message='Invalid file type')

        # Save the file
        try:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return render_template('upload.html', message=f'File "{filename}" uploaded successfully!')
        except Exception as e:
            return render_template('upload.html', message=f'Error uploading file: {str(e)}')

    # If it's a GET request, render the upload form
    return render_template('upload.html', message='')


if __name__ == '__main__':
    # Create a simple upload form (upload.html) in a 'templates' folder
    # For example:
    # templates/upload.html:
    # <!DOCTYPE html>
    # <html>
    # <head>
    #     <title>File Upload</title>
    # </head>
    # <body>
    #     <h1>File Upload</h1>
    #     <form method="POST" enctype="multipart/form-data">
    #         <input type="file" name="file">
    #         <input type="submit">
    #     </form>
    #     {% if message %}
    #         <p>{{ message }}</p>
    #     {% endif %}
    # </body>
    # </html>

    app.run(debug=True)  # Enable debug mode for development