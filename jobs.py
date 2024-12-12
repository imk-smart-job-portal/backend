from fastapi import APIRouter, HTTPException, Depends, Header
from database import get_db_connection
from auth import verify_jwt

router = APIRouter()

# Create a Job
@router.post("/jobs")
def create_job(title: str, description: str, experience_level: str, education_level: str,
               career_level: str, employment_type: str,
               token: dict = Depends(verify_jwt)):  # Token is extracted automatically
    company_id = token['company_id']
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO jobs (company_id, title, description, experience_level, 
                                  education_level, career_level, employment_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, title, description, experience_level, education_level, 
                  career_level, employment_type))
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
                "required_skills": job["required_skills"]
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
                "required_skills": job["required_skills"]
            }
        else:
            raise HTTPException(status_code=404, detail="Job not found")

# Update a Job
@router.put("/jobs/{job_id}")
def update_job(job_id: int, title: str, description: str, experience_level: str, 
               education_level: str, career_level: str, employment_type: str, 
               required_skills: str, token: dict = Depends(verify_jwt)):  # Token is extracted automatically
    company_id = token['company_id']
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ? AND company_id = ?', (job_id, company_id))
        job = cursor.fetchone()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found or access denied")

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
