#!/usr/bin/env python3
"""
Extract courses from MDC PDFs and upload to DynamoDB
This script processes PDFs and populates the courses array for each program
"""

import json
import os
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime

# Get project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdftotext (more reliable than PyPDF2)"""
    try:
        # Try using pdftotext first (if available)
        result = subprocess.run(
            ['pdftotext', '-layout', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Fallback: Try PyPDF2 if available
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except ImportError:
        print(f"Warning: PyPDF2 not available. Install with: pip3 install PyPDF2")
        return None
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {str(e)}")
        return None

def extract_courses_from_text(text, program_name):
    """Extract course codes and names from PDF text"""
    courses = []
    
    if not text:
        return courses
    
    # Pattern 1: Course code followed by course name
    # Examples: "ENC 1101 English Composition I" or "MAC 2311 - Calculus I"
    # Course codes are typically 2-4 letters followed by 4 digits
    patterns = [
        # Format: CODE XXXX - Course Name
        r'\b([A-Z]{2,4})\s+(\d{4})\s*[-–—]\s*([^\n]+?)(?=\n|$)',
        # Format: CODE XXXX Course Name (no dash)
        r'\b([A-Z]{2,4})\s+(\d{4})\s+([A-Z][^\n]{10,80}?)(?=\s+[A-Z]{2,4}\s+\d{4}|\n|$)',
        # Format: CODE XXXX: Course Name
        r'\b([A-Z]{2,4})\s+(\d{4})\s*:\s*([^\n]+?)(?=\n|$)',
    ]
    
    seen_courses = set()
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            course_code = f"{match.group(1).upper()} {match.group(2)}"
            course_name = match.group(3).strip()
            
            # Clean up course name
            course_name = re.sub(r'\s+', ' ', course_name)
            course_name = course_name.strip('.,;:()[]')
            
            # Skip if too short or looks invalid
            if len(course_name) < 5 or len(course_name) > 100:
                continue
            
            # Skip if we've seen this course code already
            if course_code in seen_courses:
                continue
            
            # Validate course code format
            if re.match(r'^[A-Z]{2,4}\s+\d{4}$', course_code):
                courses.append({
                    'code': course_code,
                    'name': course_name
                })
                seen_courses.add(course_code)
    
    return courses

def load_program_mapping():
    """Load program mapping from CSV to match PDF filenames to program IDs"""
    mapping = {}
    csv_path = PROJECT_ROOT / 'DataCollection' / 'pdf_download_log.csv'
    
    if not csv_path.exists():
        return mapping
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Skip header
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    major = parts[0].strip()
                    degree_type = parts[1].strip()
                    filename = parts[3].strip()
                    
                    # Create program ID (same format as upload script)
                    program_id = major.lower().replace(' ', '-').replace(',', '').replace('_', '-')
                    program_id = re.sub(r'[^a-z0-9-]', '', program_id)
                    program_id = f"{program_id}-{degree_type.lower()}"
                    
                    # Map filename to program ID
                    mapping[filename] = {
                        'programId': program_id,
                        'programName': major,
                        'degreeType': degree_type
                    }
    except Exception as e:
        print(f"Warning: Could not load CSV mapping: {str(e)}")
    
    return mapping

def get_program_id_from_filename(filename, program_mapping):
    """Extract program name and create program ID from filename using CSV mapping"""
    # Try to find in mapping first
    if filename in program_mapping:
        info = program_mapping[filename]
        return info['programId'], info['programName'], info['degreeType']
    
    # Fallback: extract from filename
    name = filename.replace('_Course_Sequence_2025.pdf', '')
    name = name.replace('_Course_list_2025.pdf', '')
    name = name.replace('_', ' ')
    
    # Determine degree type from path
    if 'Associates_in_Arts' in str(filename) or 'Associates_in_Science' in str(filename):
        degree_type = 'AA' if 'Arts' in str(filename) else 'AS'
    elif 'Bachelors' in str(filename):
        degree_type = 'BAS'
    else:
        degree_type = 'AA'  # Default
    
    program_id = name.lower().replace(' ', '-').replace(',', '').replace('_', '-')
    program_id = re.sub(r'[^a-z0-9-]', '', program_id)
    program_id = f"{program_id}-{degree_type.lower()}"
    
    return program_id, name, degree_type

def process_pdf_and_upload(pdf_path, program_mapping, aws_region='us-east-1'):
    """Process a single PDF and upload courses to DynamoDB"""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"✗ File not found: {pdf_path}")
        return False
    
    # Get program info from filename using mapping
    program_id, program_name, degree_type = get_program_id_from_filename(pdf_path.name, program_mapping)
    
    print(f"Processing: {pdf_path.name}")
    print(f"  Program ID: {program_id}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(f"  ✗ Could not extract text from PDF")
        return False
    
    # Extract courses
    courses = extract_courses_from_text(text, program_name)
    
    if not courses:
        print(f"  ⚠ No courses found in PDF")
        return False
    
    print(f"  ✓ Found {len(courses)} courses")
    
    # Get existing program data from DynamoDB
    try:
        key_json = json.dumps({'programId': {'S': program_id}})
        result = subprocess.run(
            ['aws', 'dynamodb', 'get-item', 
             '--table-name', 'MDCPrograms',
             '--key', key_json,
             '--region', aws_region],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            print(f"  ⚠ Program not found in DynamoDB: {program_id}")
            return False
        
        try:
            existing_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"  ⚠ Invalid JSON response from DynamoDB")
            return False
            
        if 'Item' not in existing_data:
            print(f"  ⚠ Program not found in DynamoDB: {program_id}")
            return False
        
        # Merge with existing courses (avoid duplicates)
        existing_courses = []
        if 'courses' in existing_data['Item'] and 'L' in existing_data['Item']['courses']:
            for course_item in existing_data['Item']['courses']['L']:
                if 'M' in course_item:
                    existing_courses.append({
                        'code': course_item['M'].get('code', {}).get('S', ''),
                        'name': course_item['M'].get('name', {}).get('S', '')
                    })
        
        # Combine and deduplicate
        all_courses = {c['code']: c for c in existing_courses}
        for course in courses:
            all_courses[course['code']] = course
        
        courses_list = list(all_courses.values())
        
        # Build DynamoDB item structure
        courses_dynamo = {
            'L': [
                {
                    'M': {
                        'code': {'S': c['code']},
                        'name': {'S': c['name']}
                    }
                }
                for c in courses_list
            ]
        }
        
        # Update the program with courses
        update_expression = "SET courses = :courses, updatedAt = :updatedAt"
        expression_values_json = json.dumps({
            ':courses': courses_dynamo,
            ':updatedAt': {'S': datetime.utcnow().isoformat() + 'Z'}
        })
        key_json = json.dumps({'programId': {'S': program_id}})
        
        result = subprocess.run(
            ['aws', 'dynamodb', 'update-item',
             '--table-name', 'MDCPrograms',
             '--key', key_json,
             '--update-expression', update_expression,
             '--expression-attribute-values', expression_values_json,
             '--region', aws_region],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"  ✅ Uploaded {len(courses_list)} courses to {program_name}")
            return True
        else:
            print(f"  ✗ Error uploading: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def main():
    """Main function to process all PDFs"""
    base_path = PROJECT_ROOT / 'DataCollection' / 'downloaded_pdfs'
    
    if not base_path.exists():
        print(f"Error: {base_path} not found!")
        return
    
    print("🔍 Extracting courses from MDC PDFs and uploading to DynamoDB...")
    print("📋 Loading program mapping from CSV...")
    program_mapping = load_program_mapping()
    print(f"   ✓ Loaded {len(program_mapping)} program mappings")
    print("=" * 60)
    
    # Process all PDFs
    pdf_files = list(base_path.rglob('*.pdf'))
    total = len(pdf_files)
    successful = 0
    failed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{total}] {pdf_file.name}")
        if process_pdf_and_upload(pdf_file, program_mapping):
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Complete!")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total: {total}")
    print("\n💡 Note: Some PDFs may need manual review if extraction failed")

if __name__ == '__main__':
    main()

