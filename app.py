from flask import Flask, render_template_string, request, jsonify
import boto3
import base64
from io import BytesIO
from PIL import Image
import os

app = Flask(__name__)

# AWS S3 Configuration (replace with your actual AWS credentials)
S3_BUCKET = 'chhayank24'
S3_REGION = 'ap-south-1'
S3_ACCESS_KEY = 'AKIAQR5EPKH3PQXSP7EI'
S3_SECRET_KEY = 'yDPESxq+7QKCWhoXcha2xKc1yWUdrirSnMFXYJ+T'

s3_client = boto3.client('s3', region_name=S3_REGION,
                         aws_access_key_id=S3_ACCESS_KEY,
                         aws_secret_access_key=S3_SECRET_KEY)

@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Capture and Upload Image</title>
        <!-- Bootstrap 5 CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f5f5f5;
                color: #333;
            }
            header {
                background-color: #c8102e;
                color: white;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-radius: 8px;
                margin-bottom: 30px;
            }
            header h1 {
                font-size: 1.8rem;
                margin: 0;
            }
            header .logo {
                max-width: 120px;
                height: auto;
                margin-right: 20px;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            }
            video, canvas {
                width: 100%;
                max-width: 600px;
                border: 2px solid #c8102e;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .filters {
                margin: 20px 0;
                display: flex;
                justify-content: space-around;
            }
            .filters button {
                background-color: #c8102e;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: 500;
            }
            .filters button:hover {
                background-color: #a60d25;
            }
            footer {
                margin-top: 40px;
                text-align: center;
                color: #666;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">
                <!-- Space for the logo -->
                <img src="https://i.postimg.cc/WbsKPNZ0/temp-Imager-WOd-Kx.avif" alt="DOSS Logo">
            </div>
            <h1>DOSS Mediatech - Capture & Upload</h1>
            <div></div>
        </header>
        <div class="container">
            <h2>Capture Your Image with Filters</h2>
            <video id="video" autoplay></video>
            <canvas id="canvas"></canvas>

            <div class="filters">
                <button onclick="applyFilter('none')">No Filter</button>
                <button onclick="applyFilter('grayscale(100%)')">Grayscale</button>
                <button onclick="applyFilter('sepia(100%)')">Sepia</button>
                <button onclick="applyFilter('invert(100%)')">Invert</button>
            </div>

            <button class="btn btn-primary" onclick="captureImage()">Capture Image</button>
            <button class="btn btn-success" onclick="uploadImage()">Upload to AWS S3</button>
        </div>

        <footer>
            <p>&copy; 2024 DOSS Mediatech</p>
        </footer>

        <script>
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const context = canvas.getContext('2d');
            let currentFilter = 'none';
            let capturedImage;

            // Access user's webcam
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    video.srcObject = stream;
                })
                .catch(err => {
                    console.error('Error accessing the camera: ', err);
                });

            // Apply filter to video
            function applyFilter(filter) {
                currentFilter = filter;
                video.style.filter = filter;
            }

            // Capture image from video
            function captureImage() {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.filter = currentFilter;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                capturedImage = canvas.toDataURL('image/png');  // Save image as base64
                console.log('Image captured');
            }

            // Upload image to AWS S3
            function uploadImage() {
                if (!capturedImage) {
                    alert("Capture an image first!");
                    return;
                }

                fetch('/upload', {
                    method: 'POST',
                    body: JSON.stringify({ image: capturedImage }),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }).then(response => {
                    if (response.ok) {
                        alert('Image uploaded successfully!');
                    } else {
                        alert('Image upload failed!');
                    }
                }).catch(err => {
                    console.error('Error uploading the image:', err);
                });
            }
        </script>
        <!-- Bootstrap 5 JS -->
        <script src=""></script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.json
    image_data = data['image'].split(",")[1]
    image = Image.open(BytesIO(base64.b64decode(image_data)))

    # Save the image locally first
    image_path = "captured_image.png"
    image.save(image_path)

    # Upload to AWS S3
    try:
        with open(image_path, "rb") as f:
            s3_client.upload_fileobj(f, S3_BUCKET, image_path)
        return jsonify({"message": "Image uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5037, use_reloader=False)
