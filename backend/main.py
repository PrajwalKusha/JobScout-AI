from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import json
from resume_parser import parse_resume_to_json
from matcher import match_job_to_resume
from indeed_scraper import scrape_jobs_api
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
# from indeed_scraper import scrape_jobs_api  # Uncomment and use if you want to connect scraping

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],  # Update if your frontend runs elsewhere
    allow_origins=["https://job-scout-ai.vercel.app"],  # Your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESUME_PATH = os.path.join(DATA_DIR, "resume.json")
JOBS_PATH = os.path.join(DATA_DIR, "jobs.json")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# --- CONFIGURATION ---
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

# --- Pydantic Model ---
class EmailRequest(BaseModel):
    email: EmailStr
    jobs: List[Dict[str, Any]]

@app.post("/upload_resume")
def upload_resume(file: UploadFile = File(...)):
    # Save uploaded PDF
    pdf_path = os.path.join(UPLOADS_DIR, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Parse resume and save as JSON
    try:
        parse_resume_to_json(pdf_path, RESUME_PATH)
        with open(RESUME_PATH) as f:
            resume_json = json.load(f)
        return {"success": True, "resume": resume_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

@app.post("/scrape_jobs")
def scrape_jobs(
    role: str = Form(...),
    location: str = Form(""),
    frequency: int = Form(5)  # default to 5
):
    try:
        jobs = scrape_jobs_api(role, location, JOBS_PATH, limit=frequency)
        return {"success": True, "jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job scraping failed: {str(e)}")

@app.get("/jobs")
def get_jobs():
    if os.path.exists(JOBS_PATH):
        with open(JOBS_PATH) as f:
            jobs = json.load(f)
        return jobs
    return []

@app.get("/resume")
def get_resume():
    if os.path.exists(RESUME_PATH):
        with open(RESUME_PATH) as f:
            resume = json.load(f)
        return resume
    return {}

@app.post("/match_job")
def match_job(job: dict):
    try:
        result = match_job_to_resume(job, RESUME_PATH)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")

# --- Helper: Summarize Jobs ---
def summarize_jobs(jobs: List[Dict[str, Any]], max_jobs: int = 5) -> str:
    summary = []
    for i, job in enumerate(jobs[:max_jobs]):
        summary.append(
            f"{i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')} ({job.get('location', 'N/A')})\n"
            f"   Salary: {job.get('salary', 'N/A')}\n"
            f"   Description: {job.get('full_description', '')[:200].replace('\\n', ' ')}...\n"
            f"   Link: {job.get('link', '')}\n"
        )
    if len(jobs) > max_jobs:
        summary.append(f"...and {len(jobs) - max_jobs} more jobs.")
    return "\n".join(summary)

# --- Email Sending Function ---
def send_email(to_email: str, subject: str, body: str):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code >= 400:
            raise Exception(f"SendGrid error: {response.status_code}")
    except Exception as e:
        print("Email sending failed:", e)
        raise HTTPException(status_code=500, detail="Failed to send email. Please try again later.")

@app.post("/send_jobs_email")
async def send_jobs_email(req: EmailRequest):
    summary = summarize_jobs(req.jobs)
    body = (
        "Here are your top job matches from JobScout:\n\n"
        f"{summary}\n\n"
        "Visit JobScout to see more details and apply. Good luck!\n"
    )
    send_email(req.email, "Your JobScout Job Matches", body)
    return {"status": "sent"}

@app.get("/")
def read_root():
    return {"JobScout": "Backend is running!"} 
