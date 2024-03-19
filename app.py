import replicate
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# if __name__ == '__main__':
#     # Bind to PORT if defined, otherwise default to 5000.
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)

# app.run(host="0.0.0.0", port=5000)

token = os.environ.get('REPLICATE_API_TOKEN')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def home():
    return render_template('index.html')

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
            url = transform_image(file)
        os.remove(filepath)
        return redirect(url)

    return 'Upload unsuccessful', 500

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
    except Exception as e:
        return str(e)  # Return error message if API call fails

if __name__ == '__main__':
    app.run(debug=True)