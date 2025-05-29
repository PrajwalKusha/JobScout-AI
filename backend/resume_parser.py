import fitz  # PyMuPDF
import requests
import json
import os
from dotenv import load_dotenv
from utils.logger import resume_logger
from utils.exceptions import PDFExtractionError, APIError, ResumeParserError
from typing import List, Dict
import re
import pdfplumber

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
        
    Raises:
        PDFExtractionError: If there's an error extracting text from the PDF
    """
    try:
        resume_logger.info(f"Attempting to extract text from PDF: {pdf_path}")
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        resume_logger.info("Successfully extracted text from PDF")
        return text
    except Exception as e:
        error_msg = f"Failed to extract text from PDF: {str(e)}"
        resume_logger.error(error_msg)
        raise PDFExtractionError(error_msg) from e

def parse_resume_with_openrouter(resume_text, api_key):
    """
    Parse resume text using OpenRouter API.
    
    Args:
        resume_text (str): Text extracted from the resume
        api_key (str): OpenRouter API key
        
    Returns:
        dict: Parsed resume data in JSON format
        
    Raises:
        APIError: If there's an error with the API request
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a resume parser. Extract key details from the following resume text and return in structured JSON format with these keys: name, email, phone, location, education, experience, skills, projects, certifications."
            },
            {
                "role": "user",
                "content": resume_text
            }
        ]
    }

    try:
        resume_logger.info("Sending request to OpenRouter API")
        response = requests.post(url, headers=headers, json=prompt)
        response.raise_for_status()  # Raise exception for bad status codes
        
        reply = response.json()
        content = reply['choices'][0]['message']['content']
        resume_logger.info("Successfully received response from OpenRouter API")
        
        try:
            parsed_json = json.loads(content)
            resume_logger.info("Successfully parsed JSON response")
            return parsed_json
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse API response as JSON: {str(e)}"
            resume_logger.error(error_msg)
            raise APIError(error_msg) from e
            
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        resume_logger.error(error_msg)
        raise APIError(error_msg) from e

def validate_parsed_resume(parsed_data):
    """
    Validate the parsed resume data.
    
    Args:
        parsed_data (dict): Parsed resume data
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ResumeParserError: If the parsed data is invalid
    """
    required_fields = ['name', 'email', 'skills', 'experience']
    missing_fields = [field for field in required_fields if field not in parsed_data]
    
    if missing_fields:
        error_msg = f"Missing required fields in parsed resume: {', '.join(missing_fields)}"
        resume_logger.error(error_msg)
        raise ResumeParserError(error_msg)
    
    return True

def parse_experience(text: str) -> List[Dict]:
    """
    Parse experience section from resume text, robustly handling multi-line/wrapped bullet points.
    Args:
        text (str): Experience section text
    Returns:
        List[Dict]: List of experience entries
    """
    experiences = []
    current_experience = None
    current_responsibility = None
    
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Skip empty lines
        if not line:
            if current_responsibility:
                # End of a responsibility
                current_experience['responsibilities'].append(current_responsibility.strip())
                current_responsibility = None
            i += 1
            continue
        # Detect company/position header (all caps, possibly with parenthesis, then location)
        if re.match(r'^[A-Z][A-Z\s&\-\.\(\)]+\s+[A-Za-z\s,]+$', line):
            if current_experience:
                if current_responsibility:
                    current_experience['responsibilities'].append(current_responsibility.strip())
                    current_responsibility = None
                experiences.append(current_experience)
            current_experience = {
                'company': line,
                'location': '',
                'position': '',
                'start_date': '',
                'end_date': '',
                'responsibilities': []
            }
            # Look ahead for location
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if re.match(r'^[A-Za-z\s,]+$', next_line):
                    current_experience['location'] = next_line
                    i += 1
            # Look ahead for position and dates
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if '–' in next_line or '-' in next_line:
                    parts = re.split(r'[–-]', next_line, maxsplit=1)
                    if len(parts) == 2:
                        current_experience['position'] = parts[0].strip()
                        date_part = parts[1].strip()
                        date_match = re.search(r'([A-Za-z]+\s+\d{4})\s*(?:-|to|–)\s*([A-Za-z]+\s+\d{4}|Present)', date_part)
                        if date_match:
                            current_experience['start_date'] = date_match.group(1)
                            current_experience['end_date'] = date_match.group(2)
                    i += 1
            current_responsibility = None
        # Bullet point (• or -)
        elif line.startswith('•') or line.startswith('-'):
            if current_responsibility:
                current_experience['responsibilities'].append(current_responsibility.strip())
            current_responsibility = line[1:].strip()
        # Continuation of previous bullet (not empty, not a new bullet, not a header)
        elif current_responsibility is not None:
            # Join with a space, unless previous line ended with a comma (for better formatting)
            if current_responsibility.endswith(','):
                current_responsibility += ' ' + line
            else:
                current_responsibility += ' ' + line
        i += 1
    # Add last responsibility and experience
    if current_experience:
        if current_responsibility:
            current_experience['responsibilities'].append(current_responsibility.strip())
        experiences.append(current_experience)
    return experiences

def split_resume_sections_with_heading(text: str):
    section_pattern = re.compile(r'^(?P<header>[A-Z][A-Z0-9 &\-\.]+):?$', re.MULTILINE)
    matches = list(section_pattern.finditer(text))
    if matches:
        first_header_start = matches[0].start()
        heading = text[:first_header_start].strip()
    else:
        heading = text.strip()
    sections = {}
    for i, match in enumerate(matches):
        header = match.group('header').strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections[header] = content
    return heading, sections

def parse_bullets(section_text: str) -> List[str]:
    bullets = []
    current_bullet = None
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('•') or stripped.startswith('-'):
            if current_bullet:
                bullets.append(current_bullet.strip())
            current_bullet = stripped[1:].strip()
        elif current_bullet is not None:
            current_bullet += ' ' + stripped
        else:
            continue
    if current_bullet:
        bullets.append(current_bullet.strip())
    return bullets

def parse_heading(heading_text: str) -> dict:
    result = {}
    lines = [line.strip() for line in heading_text.splitlines() if line.strip()]
    if lines:
        result['name'] = lines[0]
    email_match = re.search(r'([\w\.-]+@[\w\.-]+)', heading_text)
    if email_match:
        result['email'] = email_match.group(1)
    phone_match = re.search(r'(\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4})', heading_text)
    if phone_match:
        result['phone'] = phone_match.group(1)
    linkedin_match = re.search(r'(https?://[\w\.]*linkedin\.com/[^\s]+)', heading_text, re.I)
    if linkedin_match:
        result['linkedin'] = linkedin_match.group(1)
    location_match = re.search(r'([A-Za-z\s]+,\s*[A-Z]{2}\s*\d{0,5})', heading_text)
    if location_match:
        result['location'] = location_match.group(1)
    return result

def collect_bullets(lines, start_idx):
    bullets = []
    current_bullet = None
    i = start_idx
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith('•') or stripped.startswith('-'):
            if current_bullet:
                bullets.append(current_bullet.strip())
            current_bullet = stripped[1:].strip()
        elif current_bullet is not None:
            current_bullet += ' ' + stripped
        else:
            break  # End of bullets
        i += 1
    if current_bullet:
        bullets.append(current_bullet.strip())
    return bullets, i

def parse_experience_section(section_text: str):
    entries = []
    lines = [line.rstrip() for line in section_text.splitlines() if line.strip()]
    i = 0
    while i < len(lines):
        # Try to match company, location on one line, or just company
        company, location = '', ''
        company_line = lines[i]
        company_loc_match = re.match(r'^([A-Z][A-Z\s&\-\.\(\)]+)\s{2,}([A-Za-z\s,]+)$', company_line)
        if company_loc_match:
            company = company_loc_match.group(1).strip()
            location = company_loc_match.group(2).strip()
        else:
            company = company_line
        # Next line: role/title and dates
        if i + 1 < len(lines):
            role_date_line = lines[i + 1]
        else:
            break
        # Try to match role and dates
        role, dates = '', ''
        role_date_match = re.match(r'^(.+?)[\s\u2013\-]+([A-Za-z]+ \d{4} ?- ?[A-Za-z]+ \d{4}|Present|\d{4})$', role_date_line)
        if role_date_match:
            role = role_date_match.group(1).strip()
            dates = role_date_match.group(2).strip()
        else:
            # Try splitting by dash or en dash
            parts = re.split(r'[\u2013\-]', role_date_line)
            if len(parts) >= 2:
                role = parts[0].strip()
                dates = parts[1].strip()
            else:
                role = role_date_line.strip()
        i += 2
        bullets, i = collect_bullets(lines, i)
        entries.append({
            "company": company,
            "location": location,
            "role": role,
            "dates": dates,
            "bullets": bullets
        })
    return entries

def parse_projects_section(section_text: str):
    entries = []
    lines = [line.rstrip() for line in section_text.splitlines() if line.strip()]
    i = 0
    while i < len(lines):
        project_line = lines[i]
        name = tech_stack = link = ""
        # Try to extract link at the end
        link_match = re.search(r'(https?://[^\s]+|GitHub|Website)$', project_line)
        if link_match:
            link = link_match.group(1)
            project_line = project_line[:link_match.start()].strip()
        # Extract tech stack
        tech_stack_match = re.search(r'Tech Stack: ([^|]+)', project_line)
        if tech_stack_match:
            tech_stack = tech_stack_match.group(1).strip()
            name = project_line.split('|')[0].strip()
        else:
            name = project_line
        i += 1
        bullets, i = collect_bullets(lines, i)
        entries.append({
            "name": name,
            "tech_stack": tech_stack,
            "link": link,
            "bullets": bullets
        })
    return entries

def parse_education_section(section_text: str):
    entries = []
    lines = [line.rstrip() for line in section_text.splitlines() if line.strip()]
    i = 0
    while i < len(lines):
        # Try to match school, location on one line, or just school
        school, location = '', ''
        school_line = lines[i]
        school_loc_match = re.match(r'^([A-Z][A-Z\s,\-\.\(\)]+)\s{2,}([A-Za-z\s,]+)$', school_line)
        if school_loc_match:
            school = school_loc_match.group(1).strip()
            location = school_loc_match.group(2).strip()
        else:
            school = school_line
        # Next line: degree and date
        if i + 1 < len(lines):
            degree_date_line = lines[i + 1]
        else:
            break
        degree, date = '', ''
        degree_date_match = re.match(r'^(.+?),?\s+([A-Za-z]+ \d{4})$', degree_date_line)
        if degree_date_match:
            degree = degree_date_match.group(1).strip()
            date = degree_date_match.group(2).strip()
        else:
            # Try splitting by comma
            parts = degree_date_line.split(',')
            if len(parts) >= 2:
                degree = parts[0].strip()
                date = parts[1].strip()
            else:
                degree = degree_date_line.strip()
        i += 2
        bullets, i = collect_bullets(lines, i)
        entries.append({
            "school": school,
            "location": location,
            "degree": degree,
            "date": date,
            "bullets": bullets
        })
    return entries

def parse_bullets_with_wrapped_lines(section_text: str) -> List[str]:
    lines = [line.rstrip() for line in section_text.splitlines() if line.strip()]
    bullets, _ = collect_bullets(lines, 0)
    return bullets

def parse_resume_to_json(pdf_path: str, output_json: str):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    heading, sections = split_resume_sections_with_heading(text)
    parsed = parse_heading(heading)
    for section, content in sections.items():
        if section.startswith("EXPERIENCE"):
            parsed[section] = parse_experience_section(content)
        elif section.startswith("TECHNICAL PROJECTS"):
            parsed[section] = parse_projects_section(content)
        elif section.startswith("EDUCATION"):
            parsed[section] = parse_education_section(content)
        else:
            bullets = parse_bullets_with_wrapped_lines(content)
            if bullets:
                parsed[section] = bullets
            else:
                parsed[section] = content.strip()
    with open(output_json, "w") as f:
        json.dump(parsed, f, indent=4)
    print(f"Resume parsed and saved to {output_json}")

def main():
    """Main function to run the resume parser."""
    try:
        load_dotenv()
        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        PDF_PATH = "P1.pdf"

        if not OPENROUTER_API_KEY:
            raise ResumeParserError("API key not found in environment. Please set it in .env file.")
        
        if not os.path.exists(PDF_PATH):
            raise ResumeParserError(f"File {PDF_PATH} not found.")

        resume_logger.info("Starting resume parsing process")
        parse_resume_to_json(PDF_PATH, "parsed_resume.json")
        
    except ResumeParserError as e:
        resume_logger.error(f"Resume parsing failed: {str(e)}")
        raise
    except Exception as e:
        resume_logger.error(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
