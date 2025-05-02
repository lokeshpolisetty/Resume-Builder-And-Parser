import os
import json
import yaml
from pypdf import PdfReader
import google.generativeai as genai

# Load API Key from Config File
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(CONFIG_PATH) as file:
    config = yaml.safe_load(file)

API_KEY = config['GENAI_API_KEY']

# Configure API Key before using GenerativeModel
genai.configure(api_key=API_KEY)

# Initialize Google Gemini Model
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to Read PDF Text and Extract Links
def extract_text_and_links_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    links = set()  # Use a set to avoid duplicate links
    
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
        
        if "/Annots" in page:
            for annot in page["/Annots"]:
                if annot.get("/Subtype") == "/Link" and annot.get("/A"):
                    link = annot["/A"].get("/URI")
                    if link:
                        links.add(link)  # Add link to set to remove duplicates
    
    return text, list(links)  # Convert set back to list

# Function to extract ATS details from resume
def ats_extractor(resume_data, links):
    prompt = '''
    You are an expert ATS (Applicant Tracking System) parser. Extract and return ONLY the following information in the exact structure specified:
    {
        "personal_info": {
            "full_name": string,
            "email_id": string,
            "phone": string or null,
            "location": string or null,
            "github_portfolio": string or null,
            "linkedin_id": string or null
        },
        "professional_summary": string or null,
        "employment_details": [
            {
                "company": string,
                "title": string,
            "duration": string,
                "responsibilities": [string],
                "achievements": [string]
            }
        ],
        "education": [
            {
                "degree": string,
                "institution": string,
                "year": string,
                "gpa": string or null
            }
        ],
        "projects": [
            {
                "name": string,
                "description": string,
                "technologies": [string],
                "link": string or null
            }
        ],
        "technical_skills": [string],
        "soft_skills": [string],
        "certifications": [
            {
                "name": string,
                "organization": string,
                "date": string or null
            }
        ],
        "extracted_links": [string]  # Extracted links from the resume
    }
    Ensure all arrays are empty lists [] if no data is found, not null.
    '''

    try:
        response = model.generate_content(f"{prompt}\nResume:\n{resume_data}\nLinks: {links}")
        clean_response = response.text.strip()
        
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        
        extracted_data = json.loads(clean_response.strip())
        
        return extracted_data
    except json.JSONDecodeError as e:
        return {"error": "Failed to parse resume data", "details": str(e)}
    except Exception as e:
        return {"error": "Failed to process resume", "details": str(e)}

# Function to calculate ATS score
def calculate_ats_score(resume_data, extracted_data):
    score_prompt = '''
    You are an expert ATS (Applicant Tracking System) evaluator. Given the resume text and extracted data, provide a score out of 100 based on ATS compatibility. Consider factors like:
    - Presence of key sections (personal info, employment, education, skills, etc.)
    - Clarity and structure of content
    - Use of keywords and quantifiable achievements
    - Links and portfolio inclusion
    Return only a JSON object like: {"score": number}
    '''
    try:
        response = model.generate_content(f"{score_prompt}\nResume Text:\n{resume_data}\nExtracted Data:\n{json.dumps(extracted_data)}")
        clean_response = response.text.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        score_data = json.loads(clean_response.strip())
        return score_data["score"]
    except Exception as e:
        return 50  # Fallback score if GenAI fails