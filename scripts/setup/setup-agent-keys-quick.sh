#!/bin/bash
# Quick setup - non-interactive
aws ssm put-parameter \
    --name agent-api-key \
    --value "EMWW7CSbRt2opwIjN9c6MPVePKJiJWyH" \
    --type SecureString \
    --overwrite 2>/dev/null && echo "✅ Agent API key stored" || echo "⚠️  Already exists or error"

aws ssm put-parameter \
    --name agent-endpoint \
    --value "https://acx5dwqzgp76e34tk5oysuly.agents.do-ai.run" \
    --type String \
    --overwrite 2>/dev/null && echo "✅ Agent endpoint stored" || echo "⚠️  Already exists or error"
