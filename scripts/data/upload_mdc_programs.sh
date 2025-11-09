#!/bin/bash

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Script to upload MDC program data to DynamoDB using AWS CLI
# This creates the basic program structure - you'll need to add course data manually

echo "📦 Uploading MDC Programs to DynamoDB..."

# Track uploaded programs to avoid duplicates
declare -A uploaded_programs

# Read CSV and create program entries
while IFS=',' read -r major degree_type type filename url status || [ -n "$major" ]; do
    # Skip header and empty lines
    [[ "$major" == "Major" ]] && continue
    [[ -z "$major" ]] && continue
    
    # Create program ID
    program_id=$(echo "$major" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g' | sed 's/,//g')-$(echo "$degree_type" | tr '[:upper:]' '[:lower:]')
    
    # Skip if already uploaded
    if [[ -n "${uploaded_programs[$program_id]}" ]]; then
        continue
    fi
    
    # Mark as uploaded
    uploaded_programs[$program_id]=1
    
    # Create JSON item
    item=$(cat <<EOF
{
  "programId": {"S": "$program_id"},
  "programName": {"S": "$major"},
  "degreeType": {"S": "$degree_type"},
  "courses": {"L": []},
  "updatedAt": {"S": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"}
}
EOF
)
    
    # Upload to DynamoDB
    aws dynamodb put-item \
        --table-name MDCPrograms \
        --item "$item" \
        --output json > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✓ Uploaded: $major ($degree_type)"
    else
        echo "✗ Error uploading: $major"
    fi
    
done < "$PROJECT_ROOT/DataCollection/pdf_download_log.csv"

echo ""
echo "✅ Upload complete!"
echo ""
echo "⚠️  IMPORTANT: Course data needs to be added manually to each program."
echo "   Use AWS Console → DynamoDB → MDCPrograms → Edit items to add courses array."

