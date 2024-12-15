from fastapi import APIRouter, HTTPException, Depends, Header
from database import get_db_connection
from auth import verify_jwt
from genai import generate_required_skills
from datetime import datetime

router = APIRouter()

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a Job
@router.post("/jobs")
def create_job(title: str, description: str, experience_level: str, education_level: str,
               career_level: str, employment_type: str,
               token: dict = Depends(verify_jwt)):  # Token is extracted automatically
    company_id = token['company_id']

    job_description = f"Title: {title}\nDescription: {description}\nExperience Level: {experience_level}\n" \
                     f"Education Level: {education_level}\nCareer Level: {career_level}\nEmployment Type: {employment_type}"
    
    required_skills = generate_required_skills(job_description)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO jobs (company_id, title, description, experience_level, 
                                  education_level, career_level, employment_type, required_skills)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, title, description, experience_level, education_level, 
                  career_level, employment_type, required_skills))
            conn.commit()
        return {"message": "Job created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get all Jobs (with optional filters)
@router.get("/jobs")
def get_jobs():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs')
        jobs = cursor.fetchall()
        result = []
        for job in jobs:
            result.append({
                "id": job["id"],
                "company_id": job["company_id"],
                "title": job["title"],
                "description": job["description"],
                "experience_level": job["experience_level"],
                "education_level": job["education_level"],
                "career_level": job["career_level"],
                "employment_type": job["employment_type"],
            })
        return result

# Get a specific Job by ID
@router.get("/jobs/{job_id}")
def get_job_by_id(job_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        job = cursor.fetchone()
        if job:
            return {
                "id": job["id"],
                "company_id": job["company_id"],
                "title": job["title"],
                "description": job["description"],
                "experience_level": job["experience_level"],
                "education_level": job["education_level"],
                "career_level": job["career_level"],
                "employment_type": job["employment_type"],
            }
        else:
            raise HTTPException(status_code=404, detail="Job not found")

# Update a Job
@router.put("/jobs/{job_id}")
def update_job(job_id: int, title: str, description: str, experience_level: str, 
               education_level: str, career_level: str, employment_type: str, 
               token: dict = Depends(verify_jwt)):  # Token is extracted automatically
    company_id = token['company_id']
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ? AND company_id = ?', (job_id, company_id))
        job = cursor.fetchone()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found or access denied")

        job_description = f"Title: {title}\nDescription: {description}\nExperience Level: {experience_level}\n" \
                        f"Education Level: {education_level}\nCareer Level: {career_level}\nEmployment Type: {employment_type}"
        
        required_skills = generate_required_skills(job_description)

        cursor.execute('''
            UPDATE jobs SET title = ?, description = ?, experience_level = ?, education_level = ?, 
            career_level = ?, employment_type = ?, required_skills = ? WHERE id = ?
        ''', (title, description, experience_level, education_level, career_level, 
              employment_type, required_skills, job_id))
        conn.commit()
        return {"message": "Job updated successfully"}

# Delete a Job
@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, token: dict = Depends(verify_jwt)):  # Token is extracted automatically
    company_id = token['company_id']
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ? AND company_id = ?', (job_id, company_id))
        job = cursor.fetchone()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found or access denied")

        cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
        conn.commit()
        return {"message": "Job deleted successfully"}

@router.post("/apply-jobs/{job_id}")
def apply_job(job_id: int, resume_id: int, token: dict = Depends(verify_jwt)):
    applicant_id = token['applicant_id']

    try:
        application_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        application_status = "Pending"

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get required skills for the job
            cursor.execute('''
                SELECT required_skills FROM jobs WHERE id = ?
            ''', (job_id,))
            job_row = cursor.fetchone()
            if not job_row:
                raise HTTPException(status_code=404, detail="Job not found")
            job_required_skills = job_row[0]

            # Get resume's required skills
            cursor.execute('''
                SELECT required_skills FROM resumes WHERE id = ? AND applicant_id = ?
            ''', (resume_id, applicant_id))
            resume_row = cursor.fetchone()
            if not resume_row:
                raise HTTPException(status_code=404, detail="Resume not found for the applicant")
            resume_required_skills = resume_row[0]

            # Calculate similarity score
            similarity_score = calculate_cosine_similarity(job_required_skills, resume_required_skills)

            # Insert into job_applications table
            cursor.execute('''
                INSERT INTO job_applications (applicant_id, job_id, application_date, application_status, similarity_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (applicant_id, job_id, application_date, application_status, similarity_score))
            conn.commit()

        return {"message": "Job application submitted successfully", "similarity_score": similarity_score}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def calculate_cosine_similarity(job_skills: str, resume_skills: str) -> float:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Combine skills into a corpus
    corpus = [job_skills, resume_skills]
    vectorizer = CountVectorizer().fit_transform(corpus)
    vectors = vectorizer.toarray()

    # Calculate cosine similarity
    cosine_sim = cosine_similarity(vectors)
    return round(cosine_sim[0][1], 2)