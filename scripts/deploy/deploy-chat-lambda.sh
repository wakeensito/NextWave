#!/bin/bash

# Deploy Chat Lambda Function
set -e

echo "🚀 Deploying Chat Lambda Function..."

LAMBDA_FUNCTION_NAME="NextWave-Chat"
REGION="us-east-1"

# Create deployment package
echo "📦 Creating deployment package..."
cd "$(dirname "$0")"

# Clean up old package
rm -f chat-lambda-deployment.zip

# Create zip with just the chat lambda function
zip chat-lambda-deployment.zip chat_lambda_function.py

echo "✅ Package created: chat-lambda-deployment.zip"

# Check if Lambda function exists
if aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --region "$REGION" &>/dev/null; then
    echo "📤 Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --zip-file fileb://chat-lambda-deployment.zip \
        --region "$REGION"
    
    echo "⏳ Waiting for update to complete..."
    aws lambda wait function-updated \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --region "$REGION"
    
    echo "✅ Lambda function updated!"
else
    echo "❌ Lambda function '$LAMBDA_FUNCTION_NAME' not found!"
    echo "Please create it first with:"
    echo "  aws lambda create-function \\"
    echo "    --function-name $LAMBDA_FUNCTION_NAME \\"
    echo "    --runtime python3.12 \\"
    echo "    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \\"
    echo "    --handler chat_lambda_function.lambda_handler \\"
    echo "    --zip-file fileb://chat-lambda-deployment.zip \\"
    echo "    --timeout 30 \\"
    echo "    --memory-size 256 \\"
    echo "    --region $REGION"
fi

echo ""
echo "🎉 Chat Lambda deployment complete!"
echo ""
echo "Next steps:"
echo "1. Add /chat resource to API Gateway"
echo "2. Create POST method pointing to this Lambda"
echo "3. Deploy API Gateway changes"
echo "4. Update frontend with new endpoint URL"

