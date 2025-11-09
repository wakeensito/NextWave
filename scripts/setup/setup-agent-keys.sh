#!/bin/bash

# NextWave Agent API Keys Setup Script
set -e

echo "🔐 Setting up Agent API keys in Parameter Store..."

# Agent API Key (REQUIRED - sensitive)
echo ""
echo "📝 Adding Agent API Key..."
if aws ssm get-parameter --name agent-api-key &>/dev/null; then
    echo "⚠️  agent-api-key already exists"
    read -p "Update it? (y/n): " update
    if [ "$update" = "y" ]; then
        aws ssm put-parameter \
            --name agent-api-key \
            --value "EMWW7CSbRt2opwIjN9c6MPVePKJiJWyH" \
            --type SecureString \
            --overwrite
        echo "✅ Agent API key updated"
    fi
else
    aws ssm put-parameter \
        --name agent-api-key \
        --value "EMWW7CSbRt2opwIjN9c6MPVePKJiJWyH" \
        --type SecureString
    echo "✅ Agent API key stored"
fi

# Agent Endpoint (OPTIONAL - can be in code, but storing for flexibility)
echo ""
echo "📝 Adding Agent Endpoint URL..."
if aws ssm get-parameter --name agent-endpoint &>/dev/null; then
    echo "⚠️  agent-endpoint already exists"
    read -p "Update it? (y/n): " update
    if [ "$update" = "y" ]; then
        aws ssm put-parameter \
            --name agent-endpoint \
            --value "https://acx5dwqzgp76e34tk5oysuly.agents.do-ai.run" \
            --type String \
            --overwrite
        echo "✅ Agent endpoint updated"
    fi
else
    aws ssm put-parameter \
        --name agent-endpoint \
        --value "https://acx5dwqzgp76e34tk5oysuly.agents.do-ai.run" \
        --type String
    echo "✅ Agent endpoint stored"
fi

echo ""
echo "🎉 Agent API keys setup complete!"
echo ""
echo "Stored parameters:"
aws ssm describe-parameters \
    --parameter-filters "Key=Name,Values=agent-" \
    --query "Parameters[*].[Name,Type]" \
    --output table 2>/dev/null || echo "  - agent-api-key (SecureString)"
echo ""
echo "📋 Summary:"
echo "  ✅ agent-api-key: Stored as SecureString (encrypted)"
echo "  ✅ agent-endpoint: Stored as String (optional, has default)"
echo ""
echo "💡 Usage in Lambda:"
echo "  - Use get_agent_api_key() to retrieve the API key"
echo "  - Use get_agent_endpoint() to retrieve the endpoint URL"

