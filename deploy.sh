#!/bin/bash
set -e
cd ~/worldcup-pipeline
echo "Building lambda.zip..."
python3 make_zip.py
echo "Deploying to AWS Lambda..."
aws lambda update-function-code \
  --function-name miami-worldcup-lambda \
  --zip-file fileb:///home/juana/worldcup-pipeline/lambda.zip \
  --region us-east-2
echo "Done!"
