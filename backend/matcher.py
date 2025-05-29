import json
import re
from typing import Dict, Any

def extract_skills_from_resume(resume_json: Dict[str, Any]) -> set:
    # Collect all skills from the resume JSON
    skills = set()
    if 'TECHNICAL SKILLS' in resume_json:
        for skill_line in resume_json['TECHNICAL SKILLS']:
            # Split by common delimiters
            for skill in re.split(r'[,:;\-\|]', skill_line):
                skill = skill.strip()
                if skill and not skill.lower().startswith(('languages', 'tools', 'ml/analytics', 'genai')):
                    skills.add(skill.lower())
    # Optionally, add more extraction from experience/projects
    return skills

def extract_skills_from_job(job: Dict[str, Any]) -> set:
    # Extract skills from job description and title
    text = (job.get('title', '') + ' ' + job.get('full_description', '')).lower()
    # Simple skill keywords (expand as needed)
    skill_keywords = [
        'python', 'sql', 'excel', 'tableau', 'power bi', 'r', 'aws', 'docker', 'git',
        'machine learning', 'data analysis', 'business analysis', 'crm', 'tensorflow',
        'pyspark', 'gurobi', 'scikit-learn', 'matplotlib', 'css', 'html', 'jupyter', 'postgresql', 'mysql'
    ]
    found = set()
    for kw in skill_keywords:
        if kw in text:
            found.add(kw)
    return found

def match_job_to_resume(job: Dict[str, Any], resume_json_path: str) -> Dict[str, Any]:
    with open(resume_json_path) as f:
        resume_json = json.load(f)
    resume_skills = extract_skills_from_resume(resume_json)
    job_skills = extract_skills_from_job(job)
    matched_skills = resume_skills & job_skills
    missing_skills = job_skills - resume_skills
    score = len(matched_skills) / max(1, len(job_skills))
    suggestions = "Add these skills to your resume: " + ', '.join(missing_skills) if missing_skills else "Great fit!"
    return {
        "match_score": round(score, 2),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "suggestions": suggestions
    } 