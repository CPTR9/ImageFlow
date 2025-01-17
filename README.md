### 

# ImageFlow - Python WebApp to upload , AWS Lambda CI/CD Pipeline with S3, CodeBuild, CodePipeline, and DynamoDB

This project demonstrates how to create a CI/CD pipeline using AWS CodePipeline, CodeBuild, and CodeDeploy for AWS Lambda functions. The pipeline automatically deploys the latest Lambda function code whenever changes are pushed to a GitHub repository.

## Project Overview

The goal of this project is to automate the deployment of an AWS Lambda function that gets triggered when an image is uploaded to an S3 bucket, resizes the image to a 16:9 aspect ratio, uploads the processed image to a different S3 folder, and stores metadata (user name and processed image URL) in DynamoDB.

### Key Technologies

- **AWS Lambda**: Serverless compute service that executes the image processing logic.
- **AWS S3**: Storage service used to store both the uploaded and processed images.
- **AWS DynamoDB**: NoSQL database to store metadata, such as user name and the URL of the processed image.
- **AWS CodePipeline**: Orchestrates the CI/CD pipeline, automating the build and deployment process.
- **AWS CodeBuild**: Compiles and packages the Lambda function.
- **AWS CodeDeploy (via CloudFormation)**: Deploys the Lambda function using AWS SAM templates.
- **AWS SAM (Serverless Application Model)**: Used to define and deploy serverless resources such as Lambda functions.
- **GitHub**: Hosts the source code repository and triggers the pipeline on code changes.
- **Pillow**: Python image processing library used in Lambda to resize images.

## Folder Structure

```
/lambda-project
  ├── lambda_function.py    # Main Lambda function code
  ├── requirements.txt      # Python dependencies (boto3, Pillow)
  ├── buildspec.yml         # Build specification for AWS CodeBuild
  └── template.yml          # AWS SAM template for Lambda deployment
```

### Key Files

- **`lambda_function.py`**: The core of the Lambda function, handling image resizing and S3/DynamoDB interactions.
- **`requirements.txt`**: Specifies the Python packages (like Pillow) that are required for the Lambda function.
- **`buildspec.yml`**: Defines the build steps for AWS CodeBuild, including installing dependencies, packaging, and preparing the Lambda function for deployment.
- **`template.yml`**: AWS SAM template used by CodeDeploy/CloudFormation to define the Lambda function and other resources.

## How It Works

1. **User uploads an image via a web app**.
   - The image is uploaded to the S3 bucket under the `/uploads/` folder.
   
2. **Lambda Trigger**:
   - S3 triggers an AWS Lambda function on `PUT` events in the `/uploads/` folder.
   - The Lambda function downloads the image, resizes it to a 16:9 aspect ratio, and uploads the processed image to the `/processed/` folder in the same S3 bucket.
   - The Lambda function also stores the user’s name and the URL of the processed image in DynamoDB.

3. **CI/CD Pipeline**:
   - **CodePipeline** monitors the GitHub repository for changes. When a new commit is pushed, it triggers the pipeline.
   - **CodeBuild** pulls the latest code, installs dependencies (via `requirements.txt`), and packages the Lambda function using AWS SAM.
   - **CodeDeploy** (via CloudFormation) deploys the Lambda function, updating the function code and other resources defined in `template.yml`.

## CI/CD Pipeline Overview

1. **Source Stage (GitHub)**:
   - The pipeline is triggered when new code is pushed to the GitHub repository.
   
2. **Build Stage (CodeBuild)**:
   - CodeBuild installs necessary dependencies (`boto3`, `Pillow`) and packages the Lambda function using the AWS Serverless Application Model (SAM).
   
3. **Deploy Stage (CodeDeploy)**:
   - AWS CodeDeploy deploys the Lambda function by using CloudFormation to manage and update the stack based on the SAM template (`template.yml`).

## Prerequisites

Before running the pipeline, make sure you have the following:

1. **AWS IAM Role**: Ensure that your IAM role has sufficient permissions for S3, Lambda, DynamoDB, CodeBuild, CodePipeline, and CodeDeploy.
2. **AWS S3 Bucket**: The bucket should be set up to store the original and processed images.
3. **DynamoDB Table**: Create a DynamoDB table to store metadata (user name and processed image URL).
4. **GitHub Repository**: Your Lambda function code should be stored in a GitHub repository.
5. **AWS CLI**: Make sure the AWS CLI is configured with the necessary credentials to deploy and interact with AWS services.

### Setting Up S3 Bucket Permissions

Ensure your S3 bucket has the appropriate permissions to trigger Lambda and allow read/write access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

### DynamoDB Permissions

The IAM role must also have permission to write to DynamoDB:

```json
{
  "Effect": "Allow",
  "Action": "dynamodb:PutItem",
  "Resource": "arn:aws:dynamodb:region:account-id:table/your-dynamodb-table-name"
}
```

## Build and Deploy Process

1. **Commit code to GitHub**: Make changes to your Lambda function and push the changes to the main branch.
2. **CodePipeline triggered**: GitHub integration triggers CodePipeline when new changes are pushed.
3. **CodeBuild**: The `buildspec.yml` is used to install dependencies, package the Lambda function, and upload the packaged code to S3.
4. **CodeDeploy**: CloudFormation uses the `packaged.yaml` generated by CodeBuild to deploy the Lambda function.

## Example: Lambda Function

```python
import json
import boto3
from PIL import Image
from io import BytesIO

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    # Your Lambda code goes here
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
```

## Buildspec (CodeBuild)

Here’s an example of the `buildspec.yml` used to build the Lambda function:

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.8
    commands:
      - pip install -r requirements.txt -t .
  build:
    commands:
      - sam build
  post_build:
    commands:
      - sam package --output-template-file packaged.yaml --s3-bucket YOUR_S3_BUCKET_NAME

artifacts:
  type: zip
  files:
    - packaged.yaml
```

## AWS SAM Template (Lambda Deployment)

Example `template.yml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: 'AWS::Serverless-2016-10-31'
Resources:
  MyLambdaFunction:
    Type: AWS::Serverless::Function
    Properties: 
      Handler: lambda_function.lambda_handler
      Runtime: python3.8
      CodeUri: .
      MemorySize: 128
      Timeout: 100
      Policies: 
        - AWSLambdaBasicExecutionRole
Outputs:
  MyLambdaFunction:
    Description: "Lambda Function ARN"
    Value: !GetAtt MyLambdaFunction.Arn
```

## Conclusion

This project automates the deployment of AWS Lambda functions with the help of AWS CodePipeline, CodeBuild, and CodeDeploy. It offers a seamless way to manage Lambda deployments using infrastructure as code (AWS SAM and CloudFormation) and can be extended with more complex Lambda functions and other AWS resources.

---
