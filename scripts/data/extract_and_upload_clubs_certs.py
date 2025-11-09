#!/usr/bin/env python3
"""
Extract certifications from MDC PDFs and upload to DynamoDB
This script processes certificate PDFs and populates the MDCCertifications table
"""

import json
import os
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime
import csv

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

def load_certificate_mapping():
    """Load certificate mapping from CSV"""
    mapping = {}
    csv_path = PROJECT_ROOT / 'DataCollection' / 'certificate_pdf_download_log.csv'
    
    if not csv_path.exists():
        return mapping
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row.get('Filename', '').strip()
                if filename and filename != 'N/A':
                    program = row.get('Program', '').strip()
                    cert_type = row.get('Certificate Type', '').strip()
                    file_type = row.get('Type', '').strip()
                    
                    # Create certificate ID
                    cert_id = program.lower().replace(' ', '-').replace(',', '').replace('_', '-')
                    cert_id = re.sub(r'[^a-z0-9-]', '', cert_id)
                    
                    if cert_id not in mapping:
                        mapping[cert_id] = {
                            'certificateId': cert_id,
                            'certificateName': program,
                            'certificateType': cert_type,
                            'category': 'certification',
                            'files': []
                        }
                    
                    mapping[cert_id]['files'].append({
                        'filename': filename,
                        'type': file_type
                    })
    except Exception as e:
        print(f"Warning: Could not load CSV mapping: {str(e)}")
    
    return mapping

def extract_certificate_info_from_text(text, certificate_name):
    """Extract key information from certificate PDF text"""
    info = {
        'description': '',
        'requirements': [],
        'courses': [],
        'duration': '',
        'careerPaths': []
    }
    
    if not text:
        return info
    
    # Extract course codes (similar to course extraction)
    course_patterns = [
        r'\b([A-Z]{2,4})\s+(\d{4})\s*[-–—]\s*([^\n]+?)(?=\n|$)',
        r'\b([A-Z]{2,4})\s+(\d{4})\s+([A-Z][^\n]{10,80}?)(?=\s+[A-Z]{2,4}\s+\d{4}|\n|$)',
    ]
    
    seen_courses = set()
    for pattern in course_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            course_code = f"{match.group(1).upper()} {match.group(2)}"
            course_name = match.group(3).strip()
            if course_code not in seen_courses and len(course_name) > 5:
                info['courses'].append({
                    'code': course_code,
                    'name': course_name
                })
                seen_courses.add(course_code)
    
    # Extract duration (look for patterns like "X credits", "X hours", "X weeks")
    duration_match = re.search(r'(\d+)\s*(credits?|hours?|weeks?|months?|years?)', text, re.IGNORECASE)
    if duration_match:
        info['duration'] = f"{duration_match.group(1)} {duration_match.group(2)}"
    
    # Extract description (first paragraph or summary)
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
    if paragraphs:
        info['description'] = paragraphs[0][:500]  # Limit to 500 chars
    
    return info

def process_certificate_pdf_and_upload(pdf_path, certificate_mapping, aws_region='us-east-1'):
    """Process a single certificate PDF and upload to DynamoDB"""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"✗ File not found: {pdf_path}")
        return False
    
    # Find certificate info from mapping
    filename = pdf_path.name
    cert_info = None
    cert_id = None
    
    for cid, info in certificate_mapping.items():
        for file_info in info.get('files', []):
            if file_info['filename'] == filename:
                cert_info = info
                cert_id = cid
                break
        if cert_info:
            break
    
    # If not in mapping, try to extract from filename
    if not cert_info:
        name = filename.replace('_Course_Sequence_2025.pdf', '')
        name = name.replace('_Course_list_2025.pdf', '')
        name = name.replace('_', ' ')
        cert_id = name.lower().replace(' ', '-').replace(',', '').replace('_', '-')
        cert_id = re.sub(r'[^a-z0-9-]', '', cert_id)
        cert_info = {
            'certificateId': cert_id,
            'certificateName': name,
            'certificateType': 'CCC',  # Default
            'category': 'certification'
        }
    
    print(f"Processing: {pdf_path.name}")
    print(f"  Certificate ID: {cert_id}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(f"  ✗ Could not extract text from PDF")
        return False
    
    # Extract certificate information
    cert_data = extract_certificate_info_from_text(text, cert_info['certificateName'])
    
    # Determine category from folder structure
    if 'Advanced_Technical' in str(pdf_path):
        category = 'advanced_technical'
    elif 'Career_Technical' in str(pdf_path):
        category = 'career_technical'
    elif 'College_Credit' in str(pdf_path):
        category = 'college_credit'
    else:
        category = 'certification'
    
        # Build DynamoDB item
        item = {
            'certificateId': {'S': cert_id},
            'certificateName': {'S': cert_info['certificateName']},
            'certificateType': {'S': cert_info.get('certificateType', 'CCC')},
            'category': {'S': category},
            'description': {'S': cert_data['description']},
            'duration': {'S': cert_data['duration']},
            'pdfContent': {'S': text[:5000]},  # Store first 5000 chars
            'courses': {
                'L': [
                    {
                        'M': {
                            'code': {'S': c['code']},
                            'name': {'S': c['name']}
                        }
                    }
                    for c in cert_data['courses'][:20]  # Limit to 20 courses
                ]
            },
            'relatedCareers': {'SS': []},  # Will be populated by Agent 4
            'createdAt': {'S': datetime.utcnow().isoformat() + 'Z'},
            'updatedAt': {'S': datetime.utcnow().isoformat() + 'Z'}
        }
        
        # Upload to DynamoDB
        try:
            item_json = json.dumps(item)
            result = subprocess.run(
                ['aws', 'dynamodb', 'put-item',
                 '--table-name', 'MDCCertifications',
                 '--item', item_json,
                 '--region', aws_region],
                capture_output=True,
                text=True,
                timeout=10
            )
        
        if result.returncode == 0:
            print(f"  ✅ Uploaded certificate: {cert_info['certificateName']}")
            return True
        else:
            print(f"  ✗ Error uploading: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def main():
    """Main function to process all certificate PDFs"""
    base_path = PROJECT_ROOT / 'DataCollection' / 'downloaded_pdfs' / 'Certificates'
    
    if not base_path.exists():
        print(f"Error: {base_path} not found!")
        print("💡 Make sure you've pulled the latest from upstream/main")
        return
    
    print("🔍 Extracting certificates from MDC PDFs and uploading to DynamoDB...")
    print("📋 Loading certificate mapping from CSV...")
    certificate_mapping = load_certificate_mapping()
    print(f"   ✓ Loaded {len(certificate_mapping)} certificate mappings")
    print("=" * 60)
    
    # Process all PDFs
    pdf_files = list(base_path.rglob('*.pdf'))
    total = len(pdf_files)
    successful = 0
    failed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{total}] {pdf_file.name}")
        if process_certificate_pdf_and_upload(pdf_file, certificate_mapping):
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Complete!")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total: {total}")
    print("\n💡 Note: Some PDFs may need manual review if extraction failed")
    print("💡 Next step: Use Agent 4 in Lambda to match certificates to careers")
    print("💡 Table: MDCCertifications (separate from MDCPrograms)")

if __name__ == '__main__':
    main()

