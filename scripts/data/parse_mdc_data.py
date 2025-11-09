"""
Parse MDC PDFs and extract course data for DynamoDB storage
This script processes PDFs from DataCollection and creates structured JSON data
"""

import json
import os
import re
from pathlib import Path
import PyPDF2
import boto3
from botocore.exceptions import ClientError

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MDCPrograms')

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {str(e)}")
        return None

def extract_courses_from_text(text, program_name):
    """Extract course codes and names from PDF text"""
    courses = []
    
    # Pattern to match course codes like "ENC 1101", "MAC 2311", etc.
    # Course codes are typically 3-4 letters followed by 4 digits
    course_pattern = r'\b([A-Z]{2,4})\s+(\d{4})\b[:\s]*(.*?)(?=\n|$)'
    
    matches = re.finditer(course_pattern, text, re.MULTILINE)
    for match in matches:
        course_code = f"{match.group(1)} {match.group(2)}"
        course_name = match.group(3).strip()
        
        # Clean up course name (remove extra whitespace, special chars)
        course_name = re.sub(r'\s+', ' ', course_name)
        course_name = course_name.strip('.,;:')
        
        if course_name and len(course_name) > 3:  # Valid course name
            courses.append({
                'code': course_code,
                'name': course_name
            })
    
    return courses

def parse_program_name(filename):
    """Extract program name from filename"""
    # Remove file extension and common suffixes
    name = filename.replace('_Course_Sequence_2025.pdf', '')
    name = name.replace('_Course_list_2025.pdf', '')
    name = name.replace('_', ' ')
    return name

def process_pdf_directory(base_path):
    """Process all PDFs in a directory and extract course data"""
    programs_data = {}
    
    for pdf_file in Path(base_path).rglob('*.pdf'):
        program_name = parse_program_name(pdf_file.stem)
        file_type = 'sequence' if 'Sequence' in pdf_file.name else 'list'
        
        print(f"Processing: {pdf_file.name}")
        text = extract_text_from_pdf(str(pdf_file))
        
        if text:
            courses = extract_courses_from_text(text, program_name)
            
            if program_name not in programs_data:
                programs_data[program_name] = {
                    'programName': program_name,
                    'degreeType': 'Associate' if 'Associates' in str(pdf_file.parent) else 'Bachelor',
                    'courses': [],
                    'courseSequence': [],
                    'courseList': []
                }
            
            if file_type == 'sequence':
                programs_data[program_name]['courseSequence'] = courses
            else:
                programs_data[program_name]['courseList'] = courses
            
            # Merge unique courses
            all_courses = programs_data[program_name]['courses']
            for course in courses:
                if not any(c['code'] == course['code'] for c in all_courses):
                    all_courses.append(course)
    
    return programs_data

def upload_to_dynamodb(programs_data):
    """Upload parsed program data to DynamoDB"""
    for program_name, program_data in programs_data.items():
        try:
            # Create program ID (lowercase, replace spaces with hyphens)
            program_id = program_name.lower().replace(' ', '-').replace(',', '')
            
            item = {
                'programId': program_id,
                'programName': program_data['programName'],
                'degreeType': program_data['degreeType'],
                'courses': program_data['courses'],
                'courseSequence': program_data.get('courseSequence', []),
                'courseList': program_data.get('courseList', []),
                'updatedAt': datetime.utcnow().isoformat()
            }
            
            table.put_item(Item=item)
            print(f"✓ Uploaded: {program_name} ({len(program_data['courses'])} courses)")
            
        except ClientError as e:
            print(f"✗ Error uploading {program_name}: {str(e)}")

def main():
    """Main function to process all MDC data"""
    base_path = PROJECT_ROOT / 'DataCollection' / 'downloaded_pdfs'
    
    if not base_path.exists():
        print(f"Error: {base_path} not found!")
        return
    
    print("Starting MDC data parsing...")
    programs_data = process_pdf_directory(base_path)
    
    print(f"\nFound {len(programs_data)} programs")
    print("\nUploading to DynamoDB...")
    upload_to_dynamodb(programs_data)
    
    print("\n✓ Complete! MDC data uploaded to DynamoDB")

if __name__ == '__main__':
    from datetime import datetime
    main()

