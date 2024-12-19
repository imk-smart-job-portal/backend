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
def create_job(
    title: str,
    description: str,
    experience_level: str,
    education_level: str,
    employment_type: str,
    tags: str,
    skills: str,
    min_salary: float,
    max_salary: float,
    salary_type: str,
    expiration_date: str,
    token: dict = Depends(verify_jwt)  # Token is extracted automatically
):
    company_id = token['company_id']  # Extract company ID from the token

    job_description = f"Title: {title}\nDescription: {description}\nExperience Level: {experience_level}\n" \
                     f"Education Level: {education_level}\nEmployment Type: {employment_type}\nTags: {tags}\n" \
                     f"Skills: {skills}\n"
    
    required_skills = generate_required_skills(job_description)
    job_status = "Active"


    try:
        # Establish database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Insert job data into the database
            cursor.execute('''
                INSERT INTO jobs (company_id, title, description, experience_level, 
                                  education_level, employment_type, skills, tags, 
                                  min_salary, max_salary, salary_type, expiration_date, job_status, required_skills)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, title, description, experience_level, education_level, 
                  employment_type, skills, tags, min_salary, max_salary, salary_type, expiration_date, job_status, required_skills))
            conn.commit()
        return {"message": "Job created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get all Jobs (with optional filters)
@router.get("/jobs")
def get_jobs(token: dict = Depends(verify_jwt)):
    company_id = token["company_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                jobs.id AS job_id, 
                jobs.company_id, 
                jobs.title, 
                jobs.employment_type,
                jobs.job_status,
                jobs.expiration_date,
                companies.name AS company_name, 
                companies.email AS company_email,
                companies.phone_number AS company_phone_number,
                (
                    SELECT COUNT(*) 
                    FROM job_applications 
                    WHERE job_applications.job_id = jobs.id
                ) AS total_applications
            FROM 
                jobs
            JOIN 
                companies 
            ON 
                jobs.company_id = companies.id
            WHERE 
                jobs.company_id = ?
        ''', (company_id,))
        jobs = cursor.fetchall()
        result = []
        for job in jobs:
            result.append({
                "id": job["job_id"],
                "company_id": job["company_id"],
                "title": job["title"],
                "employment_type": job["employment_type"],
                "status": job["job_status"],
                "expiration_date": job["expiration_date"],
                "total_applications": job["total_applications"],
                "company": {
                    "id": job["company_id"],
                    "name": job["company_name"],
                    "email": job["company_email"],
                    "phone_number": job["company_phone_number"],
                },
            })
        return result

# Get a specific Job by ID
from fastapi import HTTPException

# Get a specific Job by ID
@router.get("/jobs/{job_id}")
def get_job_by_id(job_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                jobs.id AS job_id, 
                jobs.company_id, 
                jobs.title, 
                jobs.description, 
                jobs.experience_level, 
                jobs.education_level, 
                jobs.career_level, 
                jobs.employment_type, 
                companies.name AS company_name, 
                companies.email AS company_email, 
                companies.phone_number AS company_phone_number
            FROM 
                jobs
            JOIN 
                companies 
            ON 
                jobs.company_id = companies.id
            WHERE 
                jobs.id = ?
        ''', (job_id,))
        job = cursor.fetchone()
        if job:
            return {
                "id": job["job_id"],
                "company_id": job["company_id"],
                "title": job["title"],
                "description": job["description"],
                "experience_level": job["experience_level"],
                "education_level": job["education_level"],
                "career_level": job["career_level"],
                "employment_type": job["employment_type"],
                "company": {
                    "id": job["company_id"],
                    "name": job["company_name"],
                    "email": job["company_email"],
                    "phone_number": job["company_phone_number"],
                },
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
def apply_job(job_id: int, token: dict = Depends(verify_jwt)):
    applicant_id = token['applicant_id']

    try:
        if not isinstance(applicant_id, int):
            raise HTTPException(status_code=400, detail="Invalid applicant ID")

        application_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        application_status = "Pending"

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Fetch resume ID
            cursor.execute("SELECT id FROM resumes WHERE applicant_id = ?", (applicant_id,))
            resume_row = cursor.fetchone()
            if not resume_row:
                raise HTTPException(status_code=404, detail="No resume found for the applicant")
            resume_id = resume_row[0]

            # Get required skills for the job
            cursor.execute('''
                SELECT required_skills FROM jobs WHERE id = ?
            ''', (job_id,))
            job_row = cursor.fetchone()
            if not job_row:
                raise HTTPException(status_code=404, detail="Job not found")
            job_required_skills = job_row[0]

            # Validate `job_required_skills`
            if job_required_skills is None:
                raise HTTPException(status_code=400, detail="Job does not have required skills specified")

            # Get resume's required skills
            cursor.execute('''
                SELECT required_skills FROM resumes WHERE id = ? AND applicant_id = ?
            ''', (resume_id, applicant_id))
            resume_row = cursor.fetchone()
            if not resume_row:
                raise HTTPException(status_code=404, detail="Resume not found for the applicant")
            resume_required_skills = resume_row[0]

            # Validate `resume_required_skills`
            if resume_required_skills is None:
                raise HTTPException(status_code=400, detail="Resume does not have required skills specified")

            print(f"Job Skills: {job_required_skills}, Resume Skills: {resume_required_skills}")

            # Calculate similarity score
            similarity_score = calculate_cosine_similarity(
                job_required_skills, resume_required_skills
            )

            # Insert into job_applications table
            cursor.execute('''
                INSERT INTO job_applications (applicant_id, job_id, application_date, application_status, similarity_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (applicant_id, job_id, application_date, application_status, similarity_score))
            conn.commit()

        return {"message": "Job application submitted successfully", "similarity_score": similarity_score}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/job-applied")
def job_applied(token: dict = Depends(verify_jwt)):
    applicant_id = token['applicant_id']

    try:
        if not isinstance(applicant_id, int):
            raise HTTPException(status_code=400, detail="Invalid applicant ID")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    *
                FROM 
                    job_applications 
                JOIN 
                    jobs 
                ON 
                    job_applications.job_id = jobs.id 
                JOIN 
                    companies 
                ON 
                    jobs.company_id = companies.id 
                WHERE 
                    job_applications.applicant_id = ?
            """, (applicant_id,))
            jobs = cursor.fetchall()
            if jobs:
                return jobs
    except Exception as e:
        raise HTTPException(status_code=404, detail="Jobs not found")

@router.get('/job-candidate/{job_id}')
def job_candidate(job_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                job_applications.id AS id,
                job_applications.applicant_id,
                job_applications.job_id,
                job_applications.similarity_score,
                applicants.name AS applicant_name
            FROM 
                job_applications
            JOIN
                applicants
            ON
                job_applications.applicant_id = applicants.id
            WHERE
                job_applications.job_id = ?
        """, (job_id,))

        candidates = cursor.fetchall()
        if candidates:
            return candidates
        else:
            raise HTTPException(status_code=404, detail="Candidate not found")

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