from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Define the directory where uploaded files will be saved.
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Create the directory if it doesn't exist

# Configure the upload folder for Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Handles file uploads.

    GET: Renders the upload form.
    POST: Handles the file upload, saves the file to disk, and renders a success message.
    """
    if request.method == 'POST':
        # Check if a file was included in the request
        if 'file' not in request.files:
            return render_template('upload.html', error='No file part')

        file = request.files['file']

        # Check if the file was selected
        if file.filename == '':
            return render_template('upload.html', error='No file selected')

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
    # Create a simple upload form (upload.html)
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
    app.run(debug=True)