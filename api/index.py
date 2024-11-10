from flask import Flask, render_template_string, request, jsonify
import boto3
import base64
from io import BytesIO
from PIL import Image
import os

app = Flask(__name__)

# AWS S3 Configuration (use environment variables for security)
S3_BUCKET = os.getenv('chhayank24')
S3_REGION = os.getenv('ap-south-1')
S3_ACCESS_KEY = os.getenv('AKIAQR5EPKH3PQXSP7EI')
S3_SECRET_KEY = os.getenv('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')

s3_client = boto3.client(
    's3',
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

@app.route('/')
def index():
    # HTML content as in your original code
    html_content = """ ... """  # Place your HTML content here
    return render_template_string(html_content)

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.json
    image_data = data['image'].split(",")[1]
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    image_path = "captured_image.png"
    image.save(image_path)

    try:
        with open(image_path, "rb") as f:
            s3_client.upload_fileobj(f, S3_BUCKET, image_path)
        return jsonify({"message": "Image uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Expose the app instance for Vercel
from api.index import app
