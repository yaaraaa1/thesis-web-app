import os
from io import BytesIO
import replicate
from flask import Flask, render_template, request, redirect, make_response, url_for
from werkzeug.utils import secure_filename
import numpy as np
import requests
from PIL import Image, ImageSequence

REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('thesis-web-app/static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_image(image_path):
    response = requests.get(image_path)
    response.raise_for_status()
    img_data = BytesIO(response.content)
    img = Image.open(img_data)
    return np.array(img)

@app.errorhandler(404)
def page_not_found(e):
    """User requested an invalid path"""
    html = render_template('error.html',errormsg='Page not found.'), 404
    response = make_response(html)
    return response

@app.route('/<condition>')
def home(condition):
    html = render_template('index.html',condition=condition)
    response = make_response(html)
    return response

@app.route('/upload/<condition>', methods=['GET','POST'])
def upload_file(condition):
    if 'file' not in request.files:
        print("error")
    file = request.files['file']
    if file.filename == '':
        print("error")
    start_age = request.form.get('age', type=int)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        response = ''
        if condition == "895682":
            try:
                with open(filepath, "rb") as file:
                   response = transform_image(file, "70", condition)
                os.remove(filepath)
                return redirect(response)
            except Exception as e:
                html = render_template('error.html', errormsg=str(e)), 500
                return make_response(html)
        elif condition == "604584":
            try:
                with open(filepath, "rb") as file:
                    response = transform_image(file, "default", condition)
                os.remove(filepath)
                print(response)
                gif = download_gif(response)
                start_frame = round(start_age/10)
                print(start_frame)
                end_frame = 7
                gif_path = os.path.join(app.config['UPLOAD_FOLDER'], 'progression.gif')  # Ensure this path is within your static directory
                trim_gif(gif, start_frame, end_frame, gif_path)
                return redirect(url_for('static', filename='uploads/progression.gif'))
            except Exception as e:
                html = render_template('error.html', errormsg=str(e)), 500
                return make_response(html)
        return redirect(response)

def download_gif(gif_url):
    """Download a GIF from a URL."""
    response = requests.get(gif_url)
    return Image.open(BytesIO(response.content))

def trim_gif(gif, start_frame, end_frame, output_path):
    total_frames = sum(1 for _ in ImageSequence.Iterator(gif))
    print(f"Total frames in the GIF: {total_frames}")
    """Trim a GIF to only include frames within a specified range and save the result."""
    frames = [frame.copy() for i, frame in enumerate(ImageSequence.Iterator(gif)) if start_frame <= i <= end_frame]
    frames[0].save(output_path, save_all=True, append_images=frames[1:], optimize=False, duration=gif.info['duration'], loop=0)

def transform_image(url, target_age, condition):
    try:
        output = replicate.run(
            "yuval-alaluf/sam:9222a21c181b707209ef12b5e0d7e94c994b58f01c7b2fec075d2e892362f13c",
            input={
                "image": url,
                "target_age": target_age
            }
        )
        return output
    except Exception:
        html = render_template('error.html', errormsg='No face detected. Please go back to the previous page and try again!'), 404
        return make_response(html)

if __name__ == '__main__':
    app.run(debug=True)