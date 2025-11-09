#!/bin/bash

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Improved script to upload all unique MDC programs to DynamoDB

echo "📦 Uploading all MDC Programs to DynamoDB..."

# Use Python to parse CSV and get unique programs
python3 << PYTHON_SCRIPT
import csv
import json
import subprocess
from datetime import datetime

PROJECT_ROOT = "$PROJECT_ROOT"
programs = {}

# Read CSV and get unique programs
with open(f'{PROJECT_ROOT}/DataCollection/pdf_download_log.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        major = row.get('Major', '').strip()
        degree_type = row.get('Degree Type', '').strip()
        
        if major and degree_type:
            program_id = f"{major.lower().replace(' ', '-').replace(',', '')}-{degree_type.lower()}"
            if program_id not in programs:
                programs[program_id] = {
                    'programId': program_id,
                    'programName': major,
                    'degreeType': degree_type
                }

# Upload each program
uploaded = 0
for program_id, program in programs.items():
    item = {
        'programId': {'S': program['programId']},
        'programName': {'S': program['programName']},
        'degreeType': {'S': program['degreeType']},
        'courses': {'L': []},
        'updatedAt': {'S': datetime.utcnow().isoformat() + 'Z'}
    }
    
    # Convert to JSON for AWS CLI
    item_json = json.dumps(item)
    
    # Upload using AWS CLI
    result = subprocess.run(
        ['aws', 'dynamodb', 'put-item', '--table-name', 'MDCPrograms', '--item', item_json],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✓ Uploaded: {program['programName']} ({program['degreeType']})")
        uploaded += 1
    else:
        print(f"✗ Error uploading {program['programName']}: {result.stderr}")

print(f"\n✅ Upload complete! {uploaded}/{len(programs)} programs uploaded")
PYTHON_SCRIPT

echo ""
echo "⚠️  Next step: Add course data to each program in DynamoDB"
echo "   You can do this manually via AWS Console or use a PDF parser"

