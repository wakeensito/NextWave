#!/bin/bash

# NextWave Lambda Deployment Script
set -e

echo "🚀 Deploying NextWave Lambda Function..."

# Check if Lambda function exists
if ! aws lambda get-function --function-name NextWave &>/dev/null; then
    echo "❌ Lambda function 'NextWave' not found. Please create it first in AWS Console."
    exit 1
fi

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt -t . --quiet || python3 -m pip install -r requirements.txt -t . --quiet

# Create deployment package
echo "📦 Creating deployment package..."
zip -r lambda-deployment.zip lambda_function.py boto3/ botocore/ s3transfer/ urllib3/ -x "*.pyc" "__pycache__/*" "*.dist-info/*" 2>/dev/null || true

# Upload to Lambda
echo "⬆️  Uploading to Lambda..."
aws lambda update-function-code \
  --function-name NextWave \
  --zip-file fileb://lambda-deployment.zip \
  --output json > /dev/null

echo "✅ Lambda function updated successfully!"

# Cleanup
rm -rf lambda-deployment.zip boto3/ botocore/ s3transfer/ urllib3/ *.dist-info/

echo "🎉 Deployment complete!"

