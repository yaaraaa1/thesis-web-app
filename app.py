import replicate
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os

REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET','POST'])
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
            url = transform_image(file)
        os.remove(filepath)
        return redirect(url)

def transform_image(url):
    # Use the Replicate API to transform the image
    # Assuming your environment variable is correctly set,
    # the client will automatically use your API token.
    try:
        output = replicate.run(
            "yuval-alaluf/sam:9222a21c181b707209ef12b5e0d7e94c994b58f01c7b2fec075d2e892362f13c",
            input={
                "image": url,
                "target_age": "70"
            }
        )
        return output  # Assuming 'url' is the key for the image URL in the output
    except Exception:
        return "/error"  # Return error message if API call fails

if __name__ == '__main__':
    app.run(debug=True)