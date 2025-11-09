"""
Setup script to create MDC Programs DynamoDB table and upload program data
Run this script locally (not in Lambda) to populate the table
"""

import json
import sys
import boto3
from datetime import datetime
from pathlib import Path
import csv

# Get project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

def create_mdc_programs_table():
    """Create the MDC Programs DynamoDB table if it doesn't exist"""
    try:
        table = dynamodb.create_table(
            TableName='MDCPrograms',
            KeySchema=[
                {
                    'AttributeName': 'programId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'programId',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # Free tier friendly
        )
        print("Creating table...")
        table.wait_until_exists()
        print("✓ Table 'MDCPrograms' created successfully")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("✓ Table 'MDCPrograms' already exists")
        return dynamodb.Table('MDCPrograms')
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        return None

def load_programs_from_csv():
    """Load program names from CSV logs"""
    programs = {}
    
    # Read from pdf_download_log.csv
    try:
        csv_path = PROJECT_ROOT / 'DataCollection' / 'pdf_download_log.csv'
        with open(csv_path, 'r') as f:
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
                            'degreeType': degree_type,
                            'courses': [],  # Will be populated from PDFs or manual entry
                            'updatedAt': datetime.utcnow().isoformat()
                        }
    except FileNotFoundError:
        print("CSV file not found, will create empty structure")
    
    return programs

def upload_programs_to_dynamodb(programs):
    """Upload programs to DynamoDB"""
    table = dynamodb.Table('MDCPrograms')
    
    for program_id, program_data in programs.items():
        try:
            table.put_item(Item=program_data)
            print(f"✓ Uploaded: {program_data['programName']} ({program_data['degreeType']})")
        except Exception as e:
            print(f"✗ Error uploading {program_data['programName']}: {str(e)}")

def main():
    """Main setup function"""
    print("Setting up MDC Programs DynamoDB table...")
    
    # Create table
    table = create_mdc_programs_table()
    if not table:
        return
    
    # Load programs from CSV
    print("\nLoading programs from CSV...")
    programs = load_programs_from_csv()
    
    print(f"\nFound {len(programs)} programs")
    
    # Upload to DynamoDB
    print("\nUploading to DynamoDB...")
    upload_programs_to_dynamodb(programs)
    
    print(f"\n✓ Setup complete! {len(programs)} programs uploaded to DynamoDB")
    print("\nNext steps:")
    print("1. Manually add course data to each program (or use PDF parser)")
    print("2. Update Lambda function to use MDCPrograms table")
    print("3. Test the integration")

if __name__ == '__main__':
    main()

