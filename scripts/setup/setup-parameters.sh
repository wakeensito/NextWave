#!/bin/bash

# NextWave Parameter Store Setup Script
set -e

echo "🔐 Setting up Parameter Store for NextWave..."

# Check if parameters already exist
if aws ssm get-parameter --name /nextwave/gemini-api-key &>/dev/null; then
    echo "⚠️  /nextwave/gemini-api-key already exists"
    read -p "Update it? (y/n): " update
    if [ "$update" = "y" ]; then
        aws ssm put-parameter \
            --name /nextwave/gemini-api-key \
            --value "$(read -sp 'Enter Gemini API Key: ' key; echo -n "$key")" \
            --type SecureString \
            --overwrite
        echo "✅ Gemini API key updated"
    fi
else
    read -sp "Enter Gemini API Key: " GEMINI_KEY
    echo
    aws ssm put-parameter \
        --name /nextwave/gemini-api-key \
        --value "$GEMINI_KEY" \
        --type SecureString
    echo "✅ Gemini API key stored"
fi

# College Scorecard API Key (optional)
read -p "Add College Scorecard API Key? (y/n): " add_scorecard
if [ "$add_scorecard" = "y" ]; then
    if aws ssm get-parameter --name /nextwave/college-scorecard-api-key &>/dev/null; then
        echo "⚠️  /nextwave/college-scorecard-api-key already exists"
        read -p "Update it? (y/n): " update
        if [ "$update" = "y" ]; then
            read -p "Enter College Scorecard API Key: " SCORECARD_KEY
            aws ssm put-parameter \
                --name /nextwave/college-scorecard-api-key \
                --value "$SCORECARD_KEY" \
                --type SecureString \
                --overwrite
            echo "✅ College Scorecard API key updated"
        fi
    else
        read -p "Enter College Scorecard API Key: " SCORECARD_KEY
        aws ssm put-parameter \
            --name /nextwave/college-scorecard-api-key \
            --value "$SCORECARD_KEY" \
            --type SecureString
        echo "✅ College Scorecard API key stored"
    fi
fi

echo ""
echo "🎉 Parameter Store setup complete!"
echo ""
echo "Stored parameters:"
aws ssm describe-parameters \
    --parameter-filters "Key=Name,Values=/nextwave/" \
    --query "Parameters[*].Name" \
    --output table 2>/dev/null || echo "  - /nextwave/gemini-api-key"

