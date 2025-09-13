from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Define the directory where uploaded files will be saved.
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Create the directory if it doesn't exist

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Handles file uploads.

    GET: Renders the upload form.
    POST: Handles the file upload, saves the file, and redirects to a success message.
    """
    if request.method == 'POST':
        # Check if a file was provided in the request
        if 'file' not in request.files:
            return render_template('upload.html', error='No file part')

        file = request.files['file']

        # Check if the file has a filename
        if file.filename == '':
            return render_template('upload.html', error='No selected file')

        # Check if the file is allowed (optional - add your allowed file types)
        # allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
        # if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        #     return render_template('upload.html', error='Invalid file type')

        # Save the file to the upload folder
        try:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('upload.html', message=f'File "{filename}" uploaded successfully!')
        except Exception as e:
            return render_template('upload.html', error=f'An error occurred: {str(e)}')

    # If it's a GET request, render the upload form
    return render_template('upload.html')


if __name__ == '__main__':
    # Create a simple HTML template for the upload form (upload.html)
    with open('templates/upload.html', 'w') as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>File Upload</title>
</head>
<body>
    <h1>File Upload</h1>
    {% if message %}
        <p style="color: green;">{{ message }}</p>
    {% endif %}
    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Upload</button>
    </form>
</body>
</html>
""")
    app.run(debug=True)  # Run the Flask app in debug mode