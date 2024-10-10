import json
import boto3
from PIL import Image
from io import BytesIO
import os
import urllib.parse

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Your DynamoDB table name
DYNAMO_TABLE_NAME = 'your-dynamodb-table-name'

def resize_image(image_data, width, height):
    with Image.open(BytesIO(image_data)) as img:
        # Resize to maintain the 16:9 ratio
        img.thumbnail((width, height))
        buffer = BytesIO()
        img.save(buffer, 'JPEG')
        buffer.seek(0)
        return buffer

def lambda_handler(event, context):
    # Get the bucket name and file name from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    # Extract the user name from the object key (assuming name is prefixed in the key)
    user_name = object_key.split('/')[1].split('_')[0]
    
    # Only process files uploaded to the "uploads/" folder
    if not object_key.startswith('uploads/'):
        return
    
    try:
        # Download the image from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_data = response['Body'].read()
        
        # Resize the image to 16:9 ratio (default size: 1280x720)
        resized_image = resize_image(image_data, 1280, 720)
        
        # Define the new S3 key for the resized image
        processed_key = object_key.replace('uploads/', 'processed/')
        
        # Upload the resized image back to S3 (processed folder)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=processed_key,
            Body=resized_image,
            ContentType='image/jpeg',
            ACL='public-read'  # Optional, to make the image publicly accessible
        )
        
        # Construct the URL of the resized image
        s3_url = f'https://{bucket_name}.s3.amazonaws.com/{processed_key}'
        
        # Save to DynamoDB
        table = dynamodb.Table(DYNAMO_TABLE_NAME)
        table.put_item(
            Item={
                'name': user_name,
                'image_url': s3_url
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Image resized and data stored successfully!')
        }
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing image: {str(e)}")
        }
