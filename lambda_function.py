import json
import boto3
import os
import re
from datetime import datetime
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
ssm = boto3.client('ssm')
table = dynamodb.Table('CareerPathways')
mdc_programs_table = dynamodb.Table('MDCPrograms')
certifications_table = dynamodb.Table('MDCCertifications')
clubs_table = dynamodb.Table('MDCClubs')

def get_gemini_api_key():
    """Retrieve Gemini API key from Secrets Manager or Parameter Store"""
    try:
        # Try Parameter Store first (cheaper) - using 'geminikey' parameter name
        response = ssm.get_parameter(
            Name='geminikey',
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        # Fallback to alternative parameter name
        try:
            response = ssm.get_parameter(
                Name='/nextwave/gemini-api-key',
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            # Fallback to Secrets Manager
            secrets_client = boto3.client('secretsmanager')
            response = secrets_client.get_secret_value(
                SecretId='MDCPartners'
            )
            secret = json.loads(response['SecretString'])
            return secret.get('GEMINI_API_KEY') or secret.get('api_key') or list(secret.values())[0]

def get_agent_api_key():
    """Retrieve Agent API key from Parameter Store"""
    try:
        # Try Parameter Store first - using 'agent-api-key' parameter name
        response = ssm.get_parameter(
            Name='agent-api-key',
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        # Fallback to alternative parameter name
        try:
            response = ssm.get_parameter(
                Name='/nextwave/agent-api-key',
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            raise Exception("Agent API key not found in Parameter Store. Please add 'agent-api-key' or '/nextwave/agent-api-key'")

def get_agent_endpoint():
    """Retrieve Agent endpoint URL from Parameter Store or use default"""
    try:
        # Try Parameter Store first
        response = ssm.get_parameter(
            Name='agent-endpoint',
            WithDecryption=False  # URL doesn't need encryption
        )
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        try:
            response = ssm.get_parameter(
                Name='/nextwave/agent-endpoint',
                WithDecryption=False
            )
            return response['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            # Agent endpoint must be configured in Parameter Store
            raise Exception("Agent endpoint not found in Parameter Store. Please set 'agent-endpoint' or '/nextwave/agent-endpoint' in SSM Parameter Store.")

def get_agent_api_key():
    """Retrieve Agent API key from Parameter Store"""
    try:
        response = ssm.get_parameter(
            Name='agent-api-key',
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        try:
            response = ssm.get_parameter(
                Name='/nextwave/agent-api-key',
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            raise Exception("Agent API key not found in Parameter Store")

def get_agent_endpoint():
    """Retrieve Agent endpoint URL from Parameter Store or use default"""
    try:
        response = ssm.get_parameter(
            Name='agent-endpoint',
            WithDecryption=False
        )
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        try:
            response = ssm.get_parameter(
                Name='/nextwave/agent-endpoint',
                WithDecryption=False
            )
            return response['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            # Agent endpoint must be configured in Parameter Store
            raise Exception("Agent endpoint not found in Parameter Store. Please set 'agent-endpoint' or '/nextwave/agent-endpoint' in SSM Parameter Store.")

def handle_chat_request(event, context):
    """Handle chatbot API requests - proxies to DigitalOcean agent"""
    try:
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body') or {}
        
        messages = body.get('messages', [])
        
        if not messages:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Messages field is required'
                })
            }
        
        # Get agent credentials
        api_key = get_agent_api_key()
        endpoint = get_agent_endpoint()
        url = f"{endpoint}/api/v1/chat/completions"
        
        # Prepare request to DigitalOcean agent
        payload = {
            "messages": messages,
            "stream": False
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Extract message from response
                if 'choices' in result and len(result['choices']) > 0:
                    message_content = result['choices'][0].get('message', {}).get('content', '')
                elif 'message' in result:
                    message_content = result['message']
                elif 'content' in result:
                    message_content = result['content']
                else:
                    message_content = json.dumps(result)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                    },
                    'body': json.dumps({
                        'message': message_content,
                        'content': message_content
                    })
                }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            print(f"HTTP Error {e.code}: {error_body}")
            return {
                'statusCode': e.code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': json.dumps({
                    'error': f'Agent API error: {error_body}'
                })
            }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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

def get_college_scorecard_api_key():
    """Retrieve College Scorecard API key from Parameter Store"""
    try:
        response = ssm.get_parameter(
            Name='collegescorecard-key',
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        try:
            response = ssm.get_parameter(
                Name='/nextwave/college-scorecard-api-key',
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            # Default to the provided key
            return 'ntgRFLSNKv02PCmynsut41GqawOSxHdDb44baMuZ'

def get_mdc_financial_data(api_key):
    """Fetch MDC financial data from College Scorecard API"""
    try:
        # MDC's IPEDS ID (you may need to verify this)
        # Miami Dade College - multiple campuses, using main campus
        # Common IPEDS IDs for MDC: 135717 (Kendall), 135726 (North), etc.
        # We'll search for Miami Dade College
        url = f"https://api.data.gov/ed/collegescorecard/v1/schools?api_key={api_key}&school.name=Miami%20Dade%20College&fields=id,school.name,cost.tuition.in_state,cost.tuition.out_of_state,cost.avg_net_price.overall,cost.avg_net_price.private,cost.roomboard.oncampus,cost.booksupply,latest.earnings.10_yrs_after_entry.median"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'results' in data and len(data['results']) > 0:
                # Get the first result (main campus)
                school = data['results'][0]
                return {
                    'tuition_in_state': school.get('cost.tuition.in_state'),
                    'tuition_out_of_state': school.get('cost.tuition.out_of_state'),
                    'avg_net_price': school.get('cost.avg_net_price.overall'),
                    'roomboard': school.get('cost.roomboard.oncampus'),
                    'booksupply': school.get('cost.booksupply'),
                    'median_earnings_10yr': school.get('latest.earnings.10_yrs_after_entry.median')
                }
        return None
    except Exception as e:
        print(f"Error fetching College Scorecard data: {str(e)}")
        return None

def get_mdc_program_data(program_name):
    """Query DynamoDB for actual MDC program data"""
    try:
        program_id = program_name.lower().replace(' ', '-').replace(',', '')
        response = mdc_programs_table.get_item(
            Key={'programId': program_id}
        )
        
        if 'Item' in response:
            return response['Item']
        
        # Try scan for partial match
        scan_response = mdc_programs_table.scan(
            FilterExpression='contains(programName, :name)',
            ExpressionAttributeValues={':name': program_name}
        )
        
        if scan_response.get('Items'):
            return scan_response['Items'][0]
        
        return None
    except Exception as e:
        print(f"Error querying MDC programs: {str(e)}")
        return None

def validate_courses_against_mdc(courses, mdc_data):
    """Validate that recommended courses actually exist in MDC data"""
    if not mdc_data or 'courses' not in mdc_data or not mdc_data['courses']:
        return courses  # Can't validate, return as-is
    
    valid_courses = []
    mdc_course_codes = {course.get('code', '').upper() for course in mdc_data['courses'] if course.get('code')}
    
    for course in courses:
        if isinstance(course, str):
            # Extract course code if format is "ENC 1101 - Course Name"
            course_code = course.split(' - ')[0].strip().upper()
            if course_code in mdc_course_codes:
                valid_courses.append(course)
            else:
                print(f"Warning: Course '{course}' not found in MDC data")
        elif isinstance(course, dict):
            course_code = course.get('code', '').upper()
            if course_code in mdc_course_codes:
                valid_courses.append(course)
    
    return valid_courses if valid_courses else courses  # Return validated or original

def get_mdc_context_for_career(career, degree_level):
    """Helper function to get MDC program data and context - shared by both agents"""
    mdc_data = None
    related_program = None
    
    # Career to program mappings (expanded for better matching including typos)
    career_mappings = {
        'doctor': 'biology', 'physician': 'biology', 'medical': 'biology', 'surgeon': 'biology',
        'lawyer': 'criminal-justice', 'attorney': 'criminal-justice', 'law': 'criminal-justice', 'legal': 'criminal-justice',
        'engineer': 'engineering', 'engineering': 'engineering',
        'architect': 'architecture', 'architecture': 'architecture',
        'nurse': 'nursing', 'nursing': 'nursing', 'nusre': 'nursing',  # Handle typo
        'business': 'business-administration', 'business administration': 'business-administration', 'business major': 'business-administration', 'accountant': 'accounting', 'accounting': 'accounting',
        'teacher': 'education', 'education': 'education', 'teaching': 'education',
        'computer': 'computer-science', 'programmer': 'computer-science', 'developer': 'computer-science', 'software': 'computer-science',
        'data': 'computer-science', 'analyst': 'computer-science', 'analytics': 'computer-science', 'data analyst': 'computer-science'
    }
    
    # Try exact match first
    career_lower = career.lower()
    for key, program in career_mappings.items():
        if key in career_lower:
            # Try to get program data - check both associate and bachelor if bachelor selected
            mdc_data = get_mdc_program_data(program)
            if mdc_data:
                related_program = mdc_data['programName']
                # If bachelor degree selected, also try to find bachelor's version
                if degree_level == 'bachelor' and mdc_data.get('degreeType', '').lower() not in ['bachelor', 'bachelors', 'ba', 'bs']:
                    # Try to find bachelor's version by scanning for bachelor programs
                    try:
                        scan_response = mdc_programs_table.scan(
                            FilterExpression='contains(programName, :name) AND (contains(degreeType, :bachelor) OR contains(programName, :bachelor))',
                            ExpressionAttributeValues={
                                ':name': program,
                                ':bachelor': 'bachelor'
                            }
                        )
                        if scan_response.get('Items'):
                            mdc_data = scan_response['Items'][0]
                            related_program = mdc_data['programName']
                    except:
                        pass  # If scan fails, use associate data
                break
    
    # If no match found, try partial word matching
    if not mdc_data:
        career_words = career_lower.split()
        for word in career_words:
            for key, program in career_mappings.items():
                if key in word or word in key:
                    mdc_data = get_mdc_program_data(program)
                    if mdc_data:
                        related_program = mdc_data['programName']
                        # If bachelor degree selected, try to find bachelor's version
                        if degree_level == 'bachelor' and mdc_data.get('degreeType', '').lower() not in ['bachelor', 'bachelors', 'ba', 'bs']:
                            try:
                                scan_response = mdc_programs_table.scan(
                                    FilterExpression='contains(programName, :name) AND (contains(degreeType, :bachelor) OR contains(programName, :bachelor))',
                                    ExpressionAttributeValues={
                                        ':name': program,
                                        ':bachelor': 'bachelor'
                                    }
                                )
                                if scan_response.get('Items'):
                                    mdc_data = scan_response['Items'][0]
                                    related_program = mdc_data['programName']
                            except:
                                pass
                        break
            if mdc_data:
                break
    
    # Build minimal MDC context if available
    mdc_context = ""
    if mdc_data and 'courses' in mdc_data and mdc_data['courses']:
        sample_courses = mdc_data['courses'][:3]  # Reduced to 3 courses
        course_examples = ", ".join([f"{c.get('code', '')}" for c in sample_courses if c.get('code')])
        mdc_context = f"MDC courses: {course_examples}. "
    
    return mdc_data, related_program, mdc_context

def get_static_financial_data(degree_level):
    """Get static financial data - no AI needed, just standard MDC costs"""
    if degree_level == 'bachelor':
        return {
            'associates': {
                'tuitionPerYear': '4000-6000',
                'housingPerMonth': '800-1200',
                'booksPerYear': '1200',
                'totalCost': '12000-18000'
            },
            'bachelors': {
                'tuitionPerYear': '8000-25000',
                'housingPerMonth': '1000-1500',
                'booksPerYear': '1500',
                'totalCost': '21000-35000'
            }
        }
    else:
        return {
            'associates': {
                'tuitionPerYear': '4000-6000',
                'housingPerMonth': '800-1200',
                'booksPerYear': '1200',
                'totalCost': '12000-18000'
            }
        }

def generate_pathway_structure(career, degree_level):
    """Agent 1: Generate pathway structure (programs, courses, duration, etc.) - NO financial/career data"""
    try:
        api_key = get_gemini_api_key()
        
        # Get MDC context (shared helper)
        mdc_data, related_program, mdc_context = get_mdc_context_for_career(career, degree_level)
        
        # Adjust prompt based on degree level
        if degree_level == 'bachelor':
            pathway_instruction = f"Generate an educational pathway to become a {career} with a Bachelor's degree at Miami Dade College (MDC). MDC offers 18 Bachelor's degree programs directly. If MDC doesn't offer a Bachelor's in this field, include transfer options to complete the Bachelor's at another university."
            bachelors_instruction = 'ALWAYS include bachelors section. If MDC offers this Bachelor\'s program, list "Miami Dade College" in universities. Otherwise, list transfer universities.'
        else:
            pathway_instruction = f"Generate an educational pathway to become a {career} starting with an Associate's degree at Miami Dade College (MDC)."
            bachelors_instruction = 'Include bachelors section if relevant for this career.'
        
        # Simplified prompt - NO financial or careerOutcomes
        # Handle non-traditional careers by suggesting related educational pathways
        prompt = f"""You are a career advisor helping a student pursue a {career} career. {pathway_instruction}

IMPORTANT: Even if "{career}" is not an exact MDC program, suggest the closest related educational pathway. For example:
- "Data Analyst" → Computer Science or Business Analytics pathway
- "Software Engineer" → Computer Science pathway  
- "Nurse Practitioner" → Nursing pathway
- "Cartoons" or "Animation" → Digital Media, Graphic Design, or Computer Science pathway
- Handle typos and creative careers by finding the closest educational match

{mdc_context}Return JSON: career, degreeLevel, note (a clear, concise 2-3 sentence personalized message as a career advisor), associates {{programs, duration, keyCourses (limit to 5 courses)}}, bachelors {{universities (use "Miami Dade College" if MDC offers this Bachelor's program, otherwise list transfer universities), duration, keyCourses (limit to 5 courses), articulationAgreements}}, masters, professionalDegree, certifications (ONLY include if absolutely required - format as array of simple names like ["Certificate Name 1", "Certificate Name 2"], max 5, keep concise 1 line each), exams (ONLY include if absolutely required - format as array of simple names, max 5, keep concise 1 line each), internships.

ALWAYS include associates section (MDC Associate's degree). {bachelors_instruction} 

CRITICAL: 
- Do NOT include certifications or exams fields at all if they are not required
- ALWAYS include note field with a personalized, clear 2-3 sentence advisor message
- Be specific and actionable in your advice"""
        
        # Use Gemini REST API - v1beta endpoint with gemini-2.5-flash
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
            with urllib.request.urlopen(req, timeout=25) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Check for errors in response
                if 'error' in result:
                    error_detail = result['error']
                    raise Exception(f"Gemini API error: {error_detail.get('message', str(error_detail))}")
                
                # Extract text from response
                if 'candidates' not in result or len(result['candidates']) == 0:
                    raise Exception(f"No candidates in Gemini response. Full response: {json.dumps(result)}")
                
                if 'content' not in result['candidates'][0] or 'parts' not in result['candidates'][0]['content']:
                    raise Exception(f"Invalid response structure. Full response: {json.dumps(result)}")
                    
                response_text = result['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            print(f"HTTP Error {e.code}: {error_body}")
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', error_body)
            except:
                error_msg = error_body
            raise Exception(f"Gemini API HTTP {e.code}: {error_msg}")
        
        # Try to extract JSON if wrapped in markdown
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        # Try to parse JSON with error handling
        try:
            pathway_data = json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            print(f"Response text (first 500 chars): {response_text[:500]}")
            # Try to find JSON object in the text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    pathway_data = json.loads(json_match.group(0))
                    print("Successfully extracted JSON from text")
                except:
                    raise Exception(f"Failed to parse JSON from Gemini response. Error: {str(e)}. Response preview: {response_text[:200]}")
            else:
                raise Exception(f"Failed to parse JSON from Gemini response. Error: {str(e)}. Response preview: {response_text[:200]}")
        
        # Remove certifications/exams if they're empty or not meaningful
        # Only keep them if they have actual content with valid entries
        if 'certifications' in pathway_data:
            if not pathway_data['certifications'] or len(pathway_data['certifications']) == 0:
                # Remove empty certifications
                del pathway_data['certifications']
            else:
                # Filter out invalid entries (empty strings, None, etc.)
                valid_certs = []
                for cert in pathway_data['certifications']:
                    if isinstance(cert, dict):
                        if cert.get('name') or cert.get('title'):
                            valid_certs.append(cert)
                    elif isinstance(cert, str) and cert.strip():
                        valid_certs.append(cert)
                if valid_certs:
                    pathway_data['certifications'] = valid_certs
                else:
                    del pathway_data['certifications']
        
        if 'exams' in pathway_data:
            if not pathway_data['exams'] or len(pathway_data['exams']) == 0:
                # Remove empty exams
                del pathway_data['exams']
            else:
                # Filter out invalid entries
                valid_exams = []
                for exam in pathway_data['exams']:
                    if isinstance(exam, dict):
                        if exam.get('name') or exam.get('title'):
                            valid_exams.append(exam)
                    elif isinstance(exam, str) and exam.strip():
                        valid_exams.append(exam)
                if valid_exams:
                    pathway_data['exams'] = valid_exams
                else:
                    del pathway_data['exams']
        
        # Limit keyCourses to 5 for both associates and bachelors
        if 'associates' in pathway_data and 'keyCourses' in pathway_data['associates']:
            if isinstance(pathway_data['associates']['keyCourses'], list):
                pathway_data['associates']['keyCourses'] = pathway_data['associates']['keyCourses'][:5]
        if 'bachelors' in pathway_data and 'keyCourses' in pathway_data['bachelors']:
            if isinstance(pathway_data['bachelors']['keyCourses'], list):
                pathway_data['bachelors']['keyCourses'] = pathway_data['bachelors']['keyCourses'][:5]
        
        # Ensure associates section always exists
        if 'associates' not in pathway_data:
            pathway_data['associates'] = {
                'programs': [f'MDC {career} Associate Program'],
                'duration': '2 years',
                'keyCourses': ['Core courses']
            }
        
        # If bachelor degree level selected, ensure bachelors section exists
        if degree_level == 'bachelor':
            if 'bachelors' not in pathway_data:
                mdc_bachelor_program = None
                if mdc_data and mdc_data.get('degreeType', '').lower() in ['bachelor', 'bachelors', 'ba', 'bs']:
                    mdc_bachelor_program = mdc_data['programName']
                
                if mdc_bachelor_program:
                    pathway_data['bachelors'] = {
                        'universities': ['Miami Dade College'],
                        'duration': '4 years',
                        'keyCourses': ['Advanced courses']
                    }
                else:
                    pathway_data['bachelors'] = {
                        'universities': ['Transfer to 4-year university'],
                        'duration': '2 years (after AA)',
                        'keyCourses': ['Advanced courses']
                    }
        
        # Optionally validate courses against MDC data (non-blocking)
        if mdc_data and 'associates' in pathway_data and 'keyCourses' in pathway_data['associates']:
            try:
                pathway_data['associates']['keyCourses'] = validate_courses_against_mdc(
                    pathway_data['associates']['keyCourses'],
                    mdc_data
                )
            except Exception as e:
                print(f"Course validation warning: {str(e)}")
        
        # Add related MDC program if found
        if related_program:
            pathway_data['relatedMDCProgram'] = related_program
        
        # Add FULL course list from MDC database for PDF generation
        if mdc_data and 'courses' in mdc_data and mdc_data['courses']:
            # Format courses as "CODE - Name" for better readability
            full_course_list = []
            for course in mdc_data['courses']:
                if isinstance(course, dict):
                    code = course.get('code', '')
                    name = course.get('name', '')
                    if code and name:
                        full_course_list.append(f"{code} - {name}")
                    elif name:
                        full_course_list.append(name)
                elif isinstance(course, str):
                    full_course_list.append(course)
            
            # Add full course list to associates section
            if 'associates' in pathway_data:
                if not isinstance(pathway_data['associates'], dict):
                    pathway_data['associates'] = {}
                pathway_data['associates']['fullCourseList'] = full_course_list

        # Ensure note (advisorNote) exists - if not, create a default one
        if 'note' not in pathway_data and 'advisorNote' in pathway_data:
            pathway_data['note'] = pathway_data['advisorNote']
        elif 'note' not in pathway_data or not pathway_data.get('note'):
            pathway_data['note'] = f"Starting with an Associate's degree at MDC provides a solid foundation for your {career} career. Focus on building core skills and maintaining strong academic performance to maximize your opportunities."

        # Always include rawResponse for successful calls
        pathway_data['rawResponse'] = response_text.strip()

        return pathway_data
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in Agent 1 (pathway structure): {error_msg}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Return minimal fallback - ensure bachelors is always a dict or None, never other types
        fallback = {
            "career": career,
            "degreeLevel": degree_level,
            "associates": {
                "programs": [f"MDC {career} Pathway"],
                "duration": "2 years",
                "keyCourses": ["Core courses"]
            },
            "certifications": [],
            "exams": [],
            "internships": []
        }
        if degree_level == 'bachelor':
            fallback["bachelors"] = {
                "universities": ["Transfer to 4-year university"],
                "duration": "2 years (after AA)",
                "keyCourses": ["Advanced courses"]
            }
        return fallback

def generate_career_outcomes(career, degree_level):
    """Agent 2: Generate career outcomes (entry-level and mid-career salaries)"""
    try:
        api_key = get_gemini_api_key()
        
        # Simple, focused prompt for career outcomes only - ALWAYS return specific jobs
        prompt = f"""You are a career advisor providing job market insights for a {career} career path.

Generate SPECIFIC, REALISTIC job titles and salary data. DO NOT use generic placeholders like f"{career} Professional" or "Job Title".

Return JSON with careerOutcomes for both associates and bachelors degrees:
{{
  "associates": {{
    "careerOutcomes": {{
      "entryLevel": [{{"title": "Specific Job Title 1", "salary": "45000-55000"}}, {{"title": "Specific Job Title 2", "salary": "48000-52000"}}],
      "midCareer": [{{"title": "Specific Job Title 3", "salary": "60000-75000"}}, {{"title": "Specific Job Title 4", "salary": "65000-80000"}}]
    }}
  }},
  "bachelors": {{
    "careerOutcomes": {{
      "entryLevel": [{{"title": "Specific Job Title 1", "salary": "55000-70000"}}, {{"title": "Specific Job Title 2", "salary": "60000-75000"}}],
      "midCareer": [{{"title": "Specific Job Title 3", "salary": "75000-110000"}}, {{"title": "Specific Job Title 4", "salary": "85000-120000"}}]
    }}
  }}
}}

CRITICAL: 
- Use REAL job titles specific to {career} (e.g., "Registered Nurse", "Software Developer", "Business Analyst")
- Include 2-3 specific job titles per category
- Use realistic salary ranges based on actual market data
- NEVER use generic placeholders"""
        
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
            with urllib.request.urlopen(req, timeout=20) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'error' in result:
                    error_detail = result['error']
                    raise Exception(f"Gemini API error: {error_detail.get('message', str(error_detail))}")
                
                if 'candidates' not in result or len(result['candidates']) == 0:
                    raise Exception(f"No candidates in Gemini response")
                
                if 'content' not in result['candidates'][0] or 'parts' not in result['candidates'][0]['content']:
                    raise Exception(f"Invalid response structure")
                    
                response_text = result['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            print(f"HTTP Error {e.code}: {error_body}")
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', error_body)
            except:
                error_msg = error_body
            raise Exception(f"Gemini API HTTP {e.code}: {error_msg}")
        
        # Extract JSON
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        # Parse JSON
        try:
            career_data = json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            print(f"JSON decode error in Agent 2: {str(e)}")
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    career_data = json.loads(json_match.group(0))
                except:
                    raise Exception(f"Failed to parse JSON from Agent 2. Error: {str(e)}")
            else:
                raise Exception(f"Failed to parse JSON from Agent 2. Error: {str(e)}")
        
        return career_data
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in Agent 2 (career outcomes): {error_msg}")
        # Return fallback career outcomes with career-specific titles
        return {
            "associates": {
                "careerOutcomes": {
                    "entryLevel": [{"title": f"{career} Assistant", "salary": "35000-45000"}],
                    "midCareer": [{"title": f"{career} Specialist", "salary": "50000-70000"}]
                }
            },
            "bachelors": {
                "careerOutcomes": {
                    "entryLevel": [{"title": f"{career} Professional", "salary": "55000-70000"}],
                    "midCareer": [{"title": f"Senior {career}", "salary": "75000-110000"}]
                }
            }
        }

def match_certifications(career, degree_level):
    """Agent 4: Match certifications AND clubs to career pathway using Gemini + DynamoDB"""
    try:
        api_key = get_gemini_api_key()
        
        # 1. Query DynamoDB for existing certifications related to this career
        related_certs = []
        related_clubs = []
        
        # Get career keywords for matching
        career_lower = career.lower()
        career_keywords = career_lower.split()
        
        # Query Certifications table
        potential_cert_matches = []
        try:
            response = certifications_table.scan()
            all_certs = response.get('Items', [])
            
            for item in all_certs:
                cert_name = item.get('certificateName', '').lower()
                description = item.get('description', '').lower()
                pdf_content = item.get('pdfContent', '').lower()
                
                # Check if any career keyword appears in certificate info
                if any(keyword in cert_name or keyword in description or keyword in pdf_content 
                       for keyword in career_keywords if len(keyword) > 3):
                    potential_cert_matches.append(item)
            
            # Limit to top 20 potential matches
            potential_cert_matches = potential_cert_matches[:20]
            
        except Exception as e:
            print(f"Error querying certifications DynamoDB: {str(e)}")
            potential_cert_matches = []
        
        # Query Clubs table
        potential_club_matches = []
        try:
            response = clubs_table.scan()
            all_clubs = response.get('Items', [])
            
            for item in all_clubs:
                club_name = item.get('clubName', '').lower()
                notes = item.get('notes', '').lower()
                school_area = item.get('schoolArea', '').lower()
                # Get suggested majors (could be a list)
                suggested_majors = item.get('suggestedMajors', [])
                majors_str = ' '.join([m.lower() if isinstance(m, str) else str(m).lower() for m in suggested_majors])
                
                # Check if any career keyword appears in club info
                if any(keyword in club_name or keyword in notes or keyword in school_area or keyword in majors_str
                       for keyword in career_keywords if len(keyword) > 3):
                    potential_club_matches.append(item)
            
            # Limit to top 20 potential matches
            potential_club_matches = potential_club_matches[:20]
            
        except Exception as e:
            print(f"Error querying clubs DynamoDB: {str(e)}")
            potential_club_matches = []
        
        # 2. Use Gemini to analyze and match BOTH certificates and clubs to career
        if potential_cert_matches or potential_club_matches:
            # Build context from DynamoDB data
            certs_context = ""
            if potential_cert_matches:
                certs_context = "Available Certificates:\n" + "\n".join([
                    f"- {item.get('certificateName', 'Unknown')}: {item.get('description', '')[:200]}"
                    for item in potential_cert_matches[:10]  # Limit to 10 for prompt
                ])
            
            clubs_context = ""
            if potential_club_matches:
                clubs_context = "\n\nAvailable Clubs:\n" + "\n".join([
                    f"- {item.get('clubName', 'Unknown')} ({item.get('campus', 'Unknown')}): {item.get('notes', '')[:150]}"
                    for item in potential_club_matches[:10]  # Limit to 10 for prompt
                ])
            
            prompt = f"""You are a career advisor helping match MDC certificates and student clubs to a {career} career path.

{certs_context}{clubs_context}

Analyze which certificates and clubs are most relevant for a student pursuing a {career} career with a {degree_level} degree.

Return JSON format:
{{
  "certifications": [
    {{
      "name": "Certificate Name",
      "relevance": "high/medium/low"
    }}
  ],
  "clubs": [
    {{
      "name": "Club Name",
      "relevance": "high/medium/low"
    }}
  ]
}}

CRITICAL REQUIREMENTS:
- Only include items with "high" or "medium" relevance
- Limit to top 5 certifications maximum
- Limit to top 5 clubs maximum
- Use ONLY the name - no descriptions, no explanations, no extra text
- Keep names concise (1 line max, typically 2-5 words)
- Example: "Medical Assistant Certificate" not "Medical Assistant Certificate which provides training in..."
- Example: "Pre-Health Sciences Club" not "Pre-Health Sciences Club which focuses on..."
"""
            
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
                with urllib.request.urlopen(req, timeout=20) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    if 'error' in result:
                        raise Exception(f"Gemini API error: {result['error']}")
                    
                    if 'candidates' not in result or len(result['candidates']) == 0:
                        raise Exception("No candidates in Gemini response")
                    
                    response_text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Extract JSON
                    if '```json' in response_text:
                        response_text = response_text.split('```json')[1].split('```')[0]
                    elif '```' in response_text:
                        response_text = response_text.split('```')[1].split('```')[0]
                    
                    # Parse JSON
                    try:
                        matches = json.loads(response_text.strip())
                        
                        # Format certifications - keep it simple and concise
                        if 'certifications' in matches:
                            related_certs = [
                                {
                                    'name': cert.get('name', '').strip()[:80],  # Limit length, keep concise
                                    'required': False  # Certificates are optional
                                }
                                for cert in matches['certifications']
                                if cert.get('relevance') in ['high', 'medium'] and cert.get('name', '').strip()
                            ][:5]  # Limit to 5
                        
                        # Format clubs - keep it simple and concise
                        if 'clubs' in matches:
                            related_clubs = [
                                {
                                    'name': club.get('name', '').strip()[:80],  # Limit length, keep concise
                                }
                                for club in matches['clubs']
                                if club.get('relevance') in ['high', 'medium'] and club.get('name', '').strip()
                            ][:5]  # Limit to 5
                            
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error in Agent 4: {str(e)}")
                        # Try to extract JSON from text
                        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                        if json_match:
                            try:
                                matches = json.loads(json_match.group(0))
                                if 'certifications' in matches:
                                    related_certs = [
                                        {'name': c.get('name', '').strip()[:80], 'required': False}
                                        for c in matches['certifications'][:5]
                                        if c.get('name', '').strip()
                                    ]
                                if 'clubs' in matches:
                                    related_clubs = [
                                        {'name': c.get('name', '').strip()[:80]}
                                        for c in matches['clubs'][:5]
                                        if c.get('name', '').strip()
                                    ]
                            except:
                                pass
                        
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
                print(f"HTTP Error in Agent 4: {e.code}: {error_body}")
            except Exception as e:
                print(f"Error calling Gemini in Agent 4: {str(e)}")
        
        return {
            'certifications': related_certs,
            'clubs': related_clubs
        }
        
    except Exception as e:
        print(f"Error in Agent 4 (certifications and clubs): {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'certifications': [],
            'clubs': []
        }

def lambda_handler(event, context):
    """Main Lambda handler - routes to pathway or chat based on path"""
    # Check the API Gateway path to route requests
    # API Gateway v1 uses 'path' or 'requestContext.resourcePath'
    path = (event.get('path', '') or 
            event.get('requestContext', {}).get('path', '') or 
            event.get('requestContext', {}).get('resourcePath', '') or 
            event.get('rawPath', ''))
    
    # Route to chat handler if path contains '/chat'
    if '/chat' in path:
        return handle_chat_request(event, context)
    
    # Otherwise, handle pathway requests (existing code)
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
        
        # Create career ID (lowercase, replace spaces with hyphens)
        # Combine career and degree level for unique key
        career_id = f"{career.lower().replace(' ', '-').replace(',', '')}-{degree_level}"
        
        # Try to get from DynamoDB first
        try:
            response = table.get_item(
                Key={
                    'careerId': career_id
                }
            )
            
            if 'Item' in response:
                # Return cached pathway
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
        
        # Not in cache, generate with 3 agents in parallel
        pathway_data = None
        career_data = None
        certifications_data = None
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all three agents to run in parallel
            pathway_future = executor.submit(generate_pathway_structure, career, degree_level)
            career_future = executor.submit(generate_career_outcomes, career, degree_level)
            certifications_future = executor.submit(match_certifications, career, degree_level)
            
            # Wait for both to complete
            try:
                pathway_data = pathway_future.result(timeout=30)
            except Exception as e:
                print(f"Agent 1 (pathway) failed: {str(e)}")
                pathway_data = {
                    "career": career,
                    "degreeLevel": degree_level,
                    "associates": {
                        "programs": [f"MDC {career} Pathway"],
                        "duration": "2 years",
                        "keyCourses": ["Core courses"]
                    },
                    "bachelors": {
                        "universities": ["Transfer to 4-year university"],
                        "duration": "2 years (after AA)",
                        "keyCourses": ["Advanced courses"]
                    } if degree_level == 'bachelor' else None,
                    "certifications": [],
                    "exams": [],
                    "internships": [],
                    "note": f"Starting with an Associate's degree at MDC provides a solid foundation for your {career} career. Focus on building core skills and maintaining strong academic performance to maximize your opportunities."
                }
            
            try:
                career_data = career_future.result(timeout=25)
            except Exception as e:
                print(f"Agent 2 (career outcomes) failed: {str(e)}")
                career_data = {
                    "associates": {
                        "careerOutcomes": {
                            "entryLevel": [{"title": f"{career} Assistant", "salary": "35000-45000"}],
                            "midCareer": [{"title": f"{career} Specialist", "salary": "50000-70000"}]
                        }
                    },
                    "bachelors": {
                        "careerOutcomes": {
                            "entryLevel": [{"title": f"{career} Professional", "salary": "55000-70000"}],
                            "midCareer": [{"title": f"Senior {career}", "salary": "75000-110000"}]
                        }
                    }
                }
            
            try:
                certifications_data = certifications_future.result(timeout=20)
            except Exception as e:
                print(f"Agent 4 (certifications) failed: {str(e)}")
                certifications_data = {
                    'certifications': []
                }
        
        # Merge results from all three agents
        # Get static financial data (no AI needed)
        financial_data = get_static_financial_data(degree_level)
        
        # Ensure pathway_data is a dict
        if not isinstance(pathway_data, dict):
            print(f"Warning: pathway_data is not a dict: {type(pathway_data)}")
            pathway_data = {}
        
        # Ensure associates always exists
        if 'associates' not in pathway_data or not pathway_data.get('associates'):
            pathway_data['associates'] = {
                'programs': [f'MDC {career} Associate Program'],
                'duration': '2 years',
                'keyCourses': ['Core courses']
            }
        
        # Ensure associates is a dict
        if not isinstance(pathway_data['associates'], dict):
            pathway_data['associates'] = {
                'programs': [f'MDC {career} Associate Program'],
                'duration': '2 years',
                'keyCourses': ['Core courses']
            }
        
        # Add financial and career outcomes to associates
        pathway_data['associates']['financial'] = financial_data.get('associates', {
            'tuitionPerYear': '4000-6000',
            'housingPerMonth': '800-1200',
            'booksPerYear': '1200',
            'totalCost': '12000-18000'
        })
        if career_data and isinstance(career_data, dict) and 'associates' in career_data and 'careerOutcomes' in career_data['associates']:
            # Validate career outcomes have actual content
            assoc_outcomes = career_data['associates']['careerOutcomes']
            if assoc_outcomes.get('entryLevel') and len(assoc_outcomes['entryLevel']) > 0:
                # Filter out generic placeholders
                valid_entry = [job for job in assoc_outcomes['entryLevel'] if job.get('title') and 'entry-level' not in job.get('title', '').lower() and 'position' not in job.get('title', '').lower() and 'job title' not in job.get('title', '').lower()]
                if valid_entry:
                    pathway_data['associates']['careerOutcomes'] = {
                        'entryLevel': valid_entry,
                        'midCareer': [job for job in assoc_outcomes.get('midCareer', []) if job.get('title') and 'mid-career' not in job.get('title', '').lower() and 'position' not in job.get('title', '').lower()] if assoc_outcomes.get('midCareer') else []
                    }
                else:
                    # Use fallback with career-specific titles
                    pathway_data['associates']['careerOutcomes'] = {
                        'entryLevel': [{"title": f"{career} Assistant", "salary": "35000-45000"}],
                        'midCareer': [{"title": f"{career} Specialist", "salary": "50000-70000"}]
                    }
            else:
                pathway_data['associates']['careerOutcomes'] = {
                    'entryLevel': [{"title": f"{career} Assistant", "salary": "35000-45000"}],
                    'midCareer': [{"title": f"{career} Specialist", "salary": "50000-70000"}]
                }
        else:
            pathway_data['associates']['careerOutcomes'] = {
                'entryLevel': [{"title": f"{career} Assistant", "salary": "35000-45000"}],
                'midCareer': [{"title": f"{career} Specialist", "salary": "50000-70000"}]
            }
        
        # Handle bachelors - only if degree_level is bachelor or if bachelors section exists
        if degree_level == 'bachelor':
            if 'bachelors' not in pathway_data or not pathway_data.get('bachelors'):
                pathway_data['bachelors'] = {
                    'universities': ['Transfer to 4-year university'],
                    'duration': '2 years (after AA)',
                    'keyCourses': ['Advanced courses']
                }
            
            # Ensure bachelors is a dict
            if not isinstance(pathway_data['bachelors'], dict):
                pathway_data['bachelors'] = {
                    'universities': ['Transfer to 4-year university'],
                    'duration': '2 years (after AA)',
                    'keyCourses': ['Advanced courses']
                }
            
            pathway_data['bachelors']['financial'] = financial_data.get('bachelors', {
                'tuitionPerYear': '8000-25000',
                'housingPerMonth': '1000-1500',
                'booksPerYear': '1500',
                'totalCost': '21000-35000'
            })
            if career_data and isinstance(career_data, dict) and 'bachelors' in career_data and 'careerOutcomes' in career_data['bachelors']:
                # Validate career outcomes have actual content
                bach_outcomes = career_data['bachelors']['careerOutcomes']
                if bach_outcomes.get('entryLevel') and len(bach_outcomes['entryLevel']) > 0:
                    # Filter out generic placeholders
                    valid_entry = [job for job in bach_outcomes['entryLevel'] if job.get('title') and 'entry-level' not in job.get('title', '').lower() and 'position' not in job.get('title', '').lower() or 'job title' not in job.get('title', '').lower()]
                    if valid_entry:
                        pathway_data['bachelors']['careerOutcomes'] = {
                            'entryLevel': valid_entry,
                            'midCareer': [job for job in bach_outcomes.get('midCareer', []) if job.get('title') and 'mid-career' not in job.get('title', '').lower() and 'position' not in job.get('title', '').lower()] if bach_outcomes.get('midCareer') else []
                        }
                    else:
                        pathway_data['bachelors']['careerOutcomes'] = {
                            'entryLevel': [{"title": f"{career} Professional", "salary": "55000-70000"}],
                            'midCareer': [{"title": f"Senior {career}", "salary": "75000-110000"}]
                        }
                else:
                    pathway_data['bachelors']['careerOutcomes'] = {
                        'entryLevel': [{"title": f"{career} Professional", "salary": "55000-70000"}],
                        'midCareer': [{"title": f"Senior {career}", "salary": "75000-110000"}]
                    }
            else:
                pathway_data['bachelors']['careerOutcomes'] = {
                    'entryLevel': [{"title": f"{career} Professional", "salary": "55000-70000"}],
                    'midCareer': [{"title": f"Senior {career}", "salary": "75000-110000"}]
                }
        elif 'bachelors' in pathway_data and pathway_data.get('bachelors'):
            # If bachelors exists but degree_level is not bachelor, still add financial/career data
            if isinstance(pathway_data['bachelors'], dict):
                pathway_data['bachelors']['financial'] = financial_data.get('bachelors', {
                    'tuitionPerYear': '8000-25000',
                    'housingPerMonth': '1000-1500',
                    'booksPerYear': '1500',
                    'totalCost': '21000-35000'
                })
                if career_data and isinstance(career_data, dict) and 'bachelors' in career_data and 'careerOutcomes' in career_data['bachelors']:
                    # Validate career outcomes have actual content
                    bach_outcomes = career_data['bachelors']['careerOutcomes']
                    if bach_outcomes.get('entryLevel') and len(bach_outcomes['entryLevel']) > 0:
                        # Filter out generic placeholders
                        valid_entry = [job for job in bach_outcomes['entryLevel'] if job.get('title') and 'entry-level' not in job.get('title', '').lower() and 'position' not in job.get('title', '').lower() and 'job title' not in job.get('title', '').lower()]
                        if valid_entry:
                            pathway_data['bachelors']['careerOutcomes'] = {
                                'entryLevel': valid_entry,
                                'midCareer': [job for job in bach_outcomes.get('midCareer', []) if job.get('title') and 'mid-career' not in job.get('title', '').lower() and 'position' not in job.get('title', '').lower()] if bach_outcomes.get('midCareer') else []
                            }
                        else:
                            pathway_data['bachelors']['careerOutcomes'] = {
                                'entryLevel': [{"title": f"{career} Professional", "salary": "55000-70000"}],
                                'midCareer': [{"title": f"Senior {career}", "salary": "75000-110000"}]
                            }
                    else:
                        pathway_data['bachelors']['careerOutcomes'] = {
                            'entryLevel': [{"title": f"{career} Professional", "salary": "55000-70000"}],
                            'midCareer': [{"title": f"Senior {career}", "salary": "75000-110000"}]
                        }
                else:
                    pathway_data['bachelors']['careerOutcomes'] = {
                        'entryLevel': [{"title": f"{career} Professional", "salary": "55000-70000"}],
                        'midCareer': [{"title": f"Senior {career}", "salary": "75000-110000"}]
                    }
        
        # Ensure required fields exist
        if 'career' not in pathway_data:
            pathway_data['career'] = career
        if 'degreeLevel' not in pathway_data:
            pathway_data['degreeLevel'] = degree_level
        
        # Ensure note exists (advisor message)
        if 'note' not in pathway_data or not pathway_data.get('note'):
            pathway_data['note'] = f"Starting with an Associate's degree at MDC provides a solid foundation for your {career} career. Focus on building core skills and maintaining strong academic performance to maximize your opportunities."
        
        # Merge Agent 4 results (certifications and clubs) into pathway data
        if certifications_data and isinstance(certifications_data, dict):
            # Merge certifications from Agent 4 (only if Agent 1 didn't provide any)
            if 'certifications' not in pathway_data or not pathway_data.get('certifications'):
                if certifications_data.get('certifications'):
                    pathway_data['certifications'] = certifications_data['certifications']
            elif pathway_data.get('certifications') and certifications_data.get('certifications'):
                # Merge both sources, avoiding duplicates
                existing_names = {c.get('name', '') for c in pathway_data['certifications'] if isinstance(c, dict)}
                for cert in certifications_data['certifications']:
                    if isinstance(cert, dict) and cert.get('name') not in existing_names:
                        pathway_data['certifications'].append(cert)
                        existing_names.add(cert.get('name', ''))
            
            # Merge clubs from Agent 4
            if certifications_data.get('clubs'):
                pathway_data['clubs'] = certifications_data['clubs']
        
        # Only add certifications/exams if they don't exist (don't override if they were deleted)
        # If they were deleted by the filtering logic above, they won't be in the dict, which is correct
        # Only add empty arrays if the field is completely missing (shouldn't happen after filtering)
        if 'certifications' not in pathway_data:
            # Don't add empty array - let it be undefined
            pass
        if 'exams' not in pathway_data:
            # Don't add empty array - let it be undefined
            pass
        
        if 'internships' not in pathway_data:
            pathway_data['internships'] = []
        
        # Final safety check - ensure associates exists and is a dict
        if 'associates' not in pathway_data or not isinstance(pathway_data.get('associates'), dict):
            print(f"CRITICAL: Associates missing or invalid for {career}, adding fallback")
            pathway_data['associates'] = {
                'programs': [f'MDC {career} Associate Program'],
                'duration': '2 years',
                'keyCourses': ['Core courses'],
                'financial': {
                    'tuitionPerYear': '4000-6000',
                    'housingPerMonth': '800-1200',
                    'booksPerYear': '1200',
                    'totalCost': '12000-18000'
                },
                'careerOutcomes': {
                    'entryLevel': [{"title": f"{career} Assistant", "salary": "35000-45000"}],
                    'midCareer': [{"title": f"{career} Specialist", "salary": "50000-70000"}]
                }
            }
        
        # Store in DynamoDB
        try:
            table.put_item(
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
        
        # Return pathway
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

