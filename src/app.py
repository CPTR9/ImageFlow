from flask import Flask , redirect , request , render_template
import boto3
import os

app = Flask(__name__)

S3_BUCKET = "imageflow899"

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
            f"uploads/{s3_file_name}",
            ExtraArgs={
                "ContentType": image.content_type
            }
        )
        return render_template('upload_result.html', success=True)
    except Exception as e:
        #print(f"Error: {e}")
        return render_template('upload_result.html', success=False , error=str(e))
    
if __name__ == '__main__':
    app.run(debug=True)

