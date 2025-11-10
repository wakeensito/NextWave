#!/usr/bin/env python3
"""
Extract clubs from MDC CSV and upload to DynamoDB
This script processes the mdc_clubrecs.csv file and populates the MDCClubs table
"""

import json
import os
import sys
import csv
import re
from pathlib import Path
from datetime import datetime

# Get project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

def create_club_id(club_name, campus):
    """Create a unique club ID from club name and campus"""
    # Combine club name and campus, make lowercase, replace spaces with hyphens
    combined = f"{club_name}-{campus}".lower()
    # Remove special characters, keep only alphanumeric and hyphens
    club_id = re.sub(r'[^a-z0-9-]', '', combined)
    # Replace multiple hyphens with single hyphen
    club_id = re.sub(r'-+', '-', club_id)
    # Remove leading/trailing hyphens
    club_id = club_id.strip('-')
    return club_id

def parse_suggested_majors(majors_str):
    """Parse suggested majors string into a list"""
    if not majors_str or majors_str.strip() == '':
        return []
    
    # Split by comma, semicolon, or slash
    majors = re.split(r'[,;/]', majors_str)
    # Clean up each major
    majors = [m.strip() for m in majors if m.strip()]
    return majors

def upload_club_to_dynamodb(club_data, aws_region='us-east-1'):
    """Upload a single club to DynamoDB"""
    import subprocess
    
    # Build DynamoDB item
    item = {
        'clubId': {'S': club_data['clubId']},
        'clubName': {'S': club_data['clubName']},
        'campus': {'S': club_data['campus']},
        'schoolArea': {'S': club_data['schoolArea']},
        'clubType': {'S': club_data['clubType']},
        'notes': {'S': club_data['notes']},
        'sourceUrl': {'S': club_data['sourceUrl']},
        'createdAt': {'S': datetime.utcnow().isoformat() + 'Z'},
        'updatedAt': {'S': datetime.utcnow().isoformat() + 'Z'}
    }
    
    # Add suggested majors as a list
    if club_data.get('suggestedMajors'):
        item['suggestedMajors'] = {
            'L': [{'S': major} for major in club_data['suggestedMajors']]
        }
    else:
        item['suggestedMajors'] = {'L': []}
    
    # Upload to DynamoDB
    try:
        item_json = json.dumps(item)
        result = subprocess.run(
            ['aws', 'dynamodb', 'put-item',
             '--table-name', 'MDCClubs',
             '--item', item_json,
             '--region', aws_region],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"  ✅ Uploaded club: {club_data['clubName']} ({club_data['campus']})")
            return True
        else:
            print(f"  ✗ Error uploading: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def main():
    """Main function to process CSV and upload clubs to DynamoDB"""
    csv_path = PROJECT_ROOT / 'resources' / 'Api Data' / 'mdc_clubrecs.csv'
    
    if not csv_path.exists():
        print(f"Error: {csv_path} not found!")
        return
    
    print("🔍 Extracting clubs from MDC CSV and uploading to DynamoDB...")
    print("=" * 60)
    
    clubs_processed = 0
    clubs_successful = 0
    clubs_failed = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                clubs_processed += 1
                club_name = row.get('Club Name', '').strip()
                campus = row.get('Campus', '').strip()
                
                if not club_name:
                    print(f"[{clubs_processed}] Skipping row with no club name")
                    continue
                
                print(f"\n[{clubs_processed}] {club_name} - {campus}")
                
                # Create club ID
                club_id = create_club_id(club_name, campus)
                print(f"  Club ID: {club_id}")
                
                # Parse suggested majors
                suggested_majors = parse_suggested_majors(row.get('Suggested Majors/Degrees', ''))
                
                # Build club data
                club_data = {
                    'clubId': club_id,
                    'clubName': club_name,
                    'campus': campus,
                    'schoolArea': row.get('School/Area', '').strip(),
                    'clubType': row.get('Club Type', '').strip(),
                    'suggestedMajors': suggested_majors,
                    'notes': row.get('Notes', '').strip(),
                    'sourceUrl': row.get('Source URL', '').strip()
                }
                
                # Upload to DynamoDB
                if upload_club_to_dynamodb(club_data):
                    clubs_successful += 1
                else:
                    clubs_failed += 1
                    
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return
    
    print("\n" + "=" * 60)
    print(f"✅ Complete!")
    print(f"   Processed: {clubs_processed}")
    print(f"   Successful: {clubs_successful}")
    print(f"   Failed: {clubs_failed}")
    print("\n💡 Next step: Use Agent 5 in Lambda to match clubs to careers")
    print("💡 Table: MDCClubs (separate from MDCCertifications)")

if __name__ == '__main__':
    main()


