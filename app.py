
from botocore.exceptions import NoCredentialsError
import replicate
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tempfile



app = Flask(__name__)

token = os.getenv('REPLICATE_API_TOKEN')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def home():
    return render_template('index.html')  # You will create this file next

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Ensure filename is secure
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        with open(filepath, "rb") as file:
            url = transform_image(file, target_age="70")
        os.remove(filepath)
        return redirect(url)

    return 'Upload unsuccessful', 500
        

def transform_image(url, target_age):
    # Use the Replicate API to transform the image
    # Assuming your environment variable is correctly set,
    # the client will automatically use your API token.
    try:
        output = replicate.run(
            "yuval-alaluf/sam:9222a21c181b707209ef12b5e0d7e94c994b58f01c7b2fec075d2e892362f13c",
            input={
                "image": url,
                "target_age": target_age
            }
        )
        return output  # Assuming 'url' is the key for the image URL in the output
    except Exception as e:
        return str(e)  # Return error message if API call fails

if __name__ == '__main__':
    app.run(debug=True)