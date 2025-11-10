#!/bin/bash
# Create DynamoDB table for MDC Clubs

echo "🔧 Creating MDCClubs DynamoDB table..."

aws dynamodb create-table \
  --table-name MDCClubs \
  --attribute-definitions \
    AttributeName=clubId,AttributeType=S \
  --key-schema \
    AttributeName=clubId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1 \
  --tags Key=Project,Value=NextWave Key=Environment,Value=Production

echo ""
echo "✅ Table creation initiated!"
echo "💡 Wait a few seconds for the table to become active, then run:"
echo "   aws dynamodb describe-table --table-name MDCClubs --region us-east-1"
echo ""
echo "📝 Next steps:"
echo "   1. Run: python3 scripts/data/extract_and_upload_clubs.py"
echo "   2. Verify data in AWS Console → DynamoDB → MDCClubs"


