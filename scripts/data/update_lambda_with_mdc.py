"""
Updated Lambda function that validates Gemini responses against real MDC data
"""

import json
import boto3
import os
from datetime import datetime
import urllib.request
import urllib.error

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
ssm = boto3.client('ssm')
pathways_table = dynamodb.Table('CareerPathways')
mdc_programs_table = dynamodb.Table('MDCPrograms')

def get_gemini_api_key():
    """Retrieve Gemini API key from Parameter Store"""
    try:
        response = ssm.get_parameter(
            Name='geminikey',
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        try:
            response = ssm.get_parameter(
                Name='/nextwave/gemini-api-key',
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            secrets_client = boto3.client('secretsmanager')
            response = secrets_client.get_secret_value(
                SecretId='MDCPartners'
            )
            secret = json.loads(response['SecretString'])
            return secret.get('GEMINI_API_KEY') or secret.get('api_key') or list(secret.values()[0])

def get_mdc_program_data(program_name):
    """Query DynamoDB for actual MDC program data"""
    try:
        # Try exact match first
        program_id = program_name.lower().replace(' ', '-').replace(',', '')
        response = mdc_programs_table.get_item(
            Key={'programId': program_id}
        )
        
        if 'Item' in response:
            return response['Item']
        
        # Try partial match (scan for programs containing keywords)
        # This is a fallback - in production, consider using a search index
        scan_response = mdc_programs_table.scan(
            FilterExpression='contains(programName, :name)',
            ExpressionAttributeValues={':name': program_name}
        )
        
        if scan_response.get('Items'):
            return scan_response['Items'][0]  # Return first match
        
        return None
    except Exception as e:
        print(f"Error querying MDC programs: {str(e)}")
        return None

def validate_courses_against_mdc(courses, mdc_data):
    """Validate that recommended courses actually exist in MDC data"""
    if not mdc_data or 'courses' not in mdc_data:
        return courses  # Can't validate, return as-is
    
    valid_courses = []
    mdc_course_codes = {course['code'].upper() for course in mdc_data['courses']}
    mdc_course_names = {course['name'].lower() for course in mdc_data['courses']}
    
    for course in courses:
        # Check if course code exists
        course_upper = course.upper() if isinstance(course, str) else course.get('code', '').upper()
        course_lower = course.lower() if isinstance(course, str) else course.get('name', '').lower()
        
        # Try to match by code (e.g., "ENC 1101")
        if course_upper in mdc_course_codes:
            # Find the full course info
            for mdc_course in mdc_data['courses']:
                if mdc_course['code'].upper() == course_upper:
                    valid_courses.append(f"{mdc_course['code']} - {mdc_course['name']}")
                    break
        # Try to match by name (partial match)
        elif any(course_lower in mdc_name or mdc_name in course_lower for mdc_name in mdc_course_names):
            # Found partial match, keep it but mark as validated
            valid_courses.append(course if isinstance(course, str) else f"{course.get('code', '')} - {course.get('name', course)}")
        else:
            # Course not found in MDC data - log but don't include
            print(f"Warning: Course '{course}' not found in MDC data for this program")
    
    return valid_courses if valid_courses else courses  # Return validated or original if none found

def generate_pathway_with_gemini(career, degree_level):
    """Call Gemini API to generate career pathway using REST API with MDC data validation"""
    try:
        api_key = get_gemini_api_key()
        
        # Try to get MDC program data for the career
        mdc_data = None
        related_program = None
        
        # Common career to program mappings
        career_mappings = {
            'doctor': 'biology',
            'physician': 'biology',
            'lawyer': 'criminal justice',
            'attorney': 'criminal justice',
            'engineer': 'engineering',
            'architect': 'architecture',
            'nurse': 'nursing',
            'business': 'business administration',
            'accountant': 'accounting',
            'teacher': 'education'
        }
        
        for key, program in career_mappings.items():
            if key in career.lower():
                mdc_data = get_mdc_program_data(program)
                if mdc_data:
                    related_program = mdc_data['programName']
                    break
        
        # Build context about MDC programs and courses
        mdc_context = ""
        if mdc_data and 'courses' in mdc_data:
            # Include sample courses in the prompt for accuracy
            sample_courses = mdc_data['courses'][:10]  # First 10 courses
            course_list = ", ".join([f"{c['code']} - {c['name']}" for c in sample_courses])
            mdc_context = f"""

IMPORTANT - Use ONLY these actual MDC courses when recommending courses for the {related_program} program:
{sample_courses}

If you need to recommend other courses, ensure they follow MDC's course code format (e.g., ENC 1101, MAC 2311, etc.) and use actual course names from MDC's curriculum."""
        
        prompt = f"""You are an experienced academic advisor at Miami Dade College (MDC) helping a student plan their educational pathway to become a {career}. Provide guidance in a supportive, encouraging, and professional advisor tone. Be warm, clear, and helpful.

IMPORTANT: If "{career}" is not a specific career that MDC offers direct programs for (like "Doctor" or "Physician"), suggest the closest related MDC program that leads to that career. For example:
- "Doctor" → Suggest "Biology" or "Pre-Med" pathway that leads to medical school
- "Lawyer" → Suggest "Pre-Law" or "Criminal Justice" pathway
- "Engineer" → Suggest specific engineering pathway (Mechanical, Civil, etc.)

{mdc_context}

As an advisor, provide a comprehensive educational pathway that includes:
1. Associate's degree (A.A./A.S.) - specific MDC programs if applicable. If the exact career isn't available at MDC, suggest the closest related program (e.g., Biology for Doctor, Pre-Engineering for Engineer)
2. Bachelor's degree (B.S.) - transfer plan and target universities
3. Master's degree (M.S.) - if relevant
4. Ph.D. or Professional degree (M.D., J.D., etc.) - if relevant
5. Required certifications and exams (e.g., FE, PE for engineering, MCAT for medical school)
6. Internships or practical experience opportunities
7. Articulation agreements from MDC to other institutions

CRITICAL: When listing courses in the "keyCourses" field, use ONLY actual MDC course codes and names. Course codes follow the format: "XXX XXXX" (e.g., "ENC 1101", "MAC 2311", "BSC 2010"). Do not make up course codes or names.

Format the response as JSON with this structure:
{{
  "career": "{career}",
  "relatedMDCProgram": "{related_program or 'The actual MDC program name that relates to this career'}",
  "degreeLevel": "{degree_level}",
  "associates": {{
    "programs": ["Specific MDC Program Name"],
    "duration": "2 years",
    "keyCourses": ["ENC 1101 - English Composition I", "MAC 2311 - College Algebra"] 
  }},
  "bachelors": {{
    "universities": ["University 1", "University 2"],
    "articulationAgreements": ["Agreement details"],
    "duration": "2 years (after AA)",
    "keyCourses": ["Course 1", "Course 2"]
  }},
  "masters": {{
    "universities": ["University 1"],
    "duration": "2 years",
    "required": true/false
  }},
  "professionalDegree": {{
    "type": "M.D./J.D./Ph.D. etc.",
    "universities": ["University 1"],
    "duration": "4 years",
    "required": true/false,
    "description": "Details about the professional degree needed"
  }},
  "certifications": [
    {{"name": "Cert Name", "required": true, "timing": "After BS"}}
  ],
  "exams": [
    {{"name": "Exam Name", "required": true, "timing": "After BS"}}
  ],
  "internships": ["Internship opportunity 1", "Internship opportunity 2"],
  "alternativePathways": ["Alternative path 1", "Alternative path 2"],
  "note": "As an advisor, provide encouraging guidance about the pathway. If the career requires a professional degree (like Doctor, Lawyer), explain the pathway clearly and supportively: Associate → Bachelor → Professional Degree. Use advisor tone - be encouraging and helpful."
}}

Tone: Write as a supportive academic advisor would speak to a student - encouraging, clear, and helpful. Use advisor language like "I recommend", "You'll want to", "This pathway will help you", etc. Be specific and realistic. Focus on MDC (Miami Dade College) programs when applicable. If the exact career isn't available at MDC, suggest the closest related program that leads to that career.

Remember: You're acting as a caring academic advisor helping a student achieve their career goals. Be encouraging and supportive throughout."""
        
        # Use Gemini REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'error' in result:
                    error_detail = result['error']
                    raise Exception(f"Gemini API error: {error_detail.get('message', str(error_detail))}")
                
                if 'candidates' not in result or len(result['candidates']) == 0:
                    raise Exception(f"No candidates in Gemini response. Full response: {json.dumps(result)}")
                
                if 'content' not in result['candidates'][0] or 'parts' not in result['candidates'][0]['content']:
                    raise Exception(f"Invalid response structure. Full response: {json.dumps(result)}")
                    
                response_text = result['candidates'][0]['content']['parts'][0]['text']
                raw_response = json.dumps(result, indent=2)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            print(f"HTTP Error {e.code}: {error_body}")
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', error_body)
            except:
                error_msg = error_body
            raise Exception(f"Gemini API HTTP {e.code}: {error_msg}")
        
        # Extract JSON from response
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        pathway_data = json.loads(response_text.strip())
        
        # Validate courses against MDC data
        if mdc_data and 'associates' in pathway_data and 'keyCourses' in pathway_data['associates']:
            pathway_data['associates']['keyCourses'] = validate_courses_against_mdc(
                pathway_data['associates']['keyCourses'],
                mdc_data
            )
        
        # Update relatedMDCProgram if we found actual data
        if related_program:
            pathway_data['relatedMDCProgram'] = related_program
        
        pathway_data['rawResponse'] = raw_response
        return pathway_data
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error calling Gemini: {error_msg}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "error": error_msg,
            "career": career,
            "degreeLevel": degree_level,
            "associates": {
                "programs": ["MDC Associate Program"],
                "duration": "2 years",
                "keyCourses": ["Core courses"]
            },
            "bachelors": {
                "universities": ["Transfer to 4-year university"],
                "duration": "2 years (after AA)",
                "keyCourses": ["Advanced courses"]
            },
            "certifications": [],
            "exams": [],
            "internships": [],
            "alternativePathways": []
        }

# Rest of lambda_handler remains the same...
def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body') or {}
        
        career = body.get('career', '').strip()
        degree_level = body.get('degreeLevel', 'associate').strip()
        
        if not career:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Career field is required'
                })
            }
        
        career_id = f"{career.lower().replace(' ', '-').replace(',', '')}-{degree_level}"
        
        # Try to get from DynamoDB first
        try:
            response = pathways_table.get_item(
                Key={'careerId': career_id}
            )
            
            if 'Item' in response:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                    },
                    'body': json.dumps({
                        'pathway': response['Item']['pathway'],
                        'cached': True,
                        'career': career
                    })
                }
        except Exception as e:
            print(f"DynamoDB read error: {str(e)}")
        
        # Generate with Gemini (now with MDC validation)
        pathway_data = generate_pathway_with_gemini(career, degree_level)
        
        # Store in DynamoDB
        try:
            pathways_table.put_item(
                Item={
                    'careerId': career_id,
                    'career': career,
                    'degreeLevel': degree_level,
                    'pathway': pathway_data,
                    'createdAt': datetime.utcnow().isoformat(),
                    'updatedAt': datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"DynamoDB write error: {str(e)}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'pathway': pathway_data,
                'cached': False,
                'career': career
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

