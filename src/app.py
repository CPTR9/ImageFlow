from flask import Flask , redirect , request , render_template
import boto3
import os

app = Flask(__name__)

S3_BUCKET = "imageflow899"
S3_ACCESS_KEY = "	AKIAZQ3DNMSI3QYOK3M2"
S3_SECRET_KEY = "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"
S3_REGION = 'us-east-1'

s3 = boto3.client('s3', aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['name']
    image = request.files['image']

    s3_file_name = f"{name}_{image.filename}"

    try:
        s3.upload_fileobj(
            image,
            S3_BUCKET,
            s3_file_name,
            ExtraArgs={
                "ACL": 'public-read',
                "ContentType": image.content_type
            }
        )
        return f"Upload Successful: {s3_file_name}!"
    except Exception as e:
        print(f"Error: {e}")
        return "Upload Failed"
    
if __name__ == '__main__':
    app.run(debug=True)

