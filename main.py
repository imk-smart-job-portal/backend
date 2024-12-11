from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
import sqlite3
from auth import hash_password, create_jwt, verify_jwt
from filters import smart_applicant_filter, smart_job_filter, smart_recommendation_skill
from database import get_db_connection, initialize_database
from jobs import router as jobs_router



load_dotenv()

app = FastAPI()


# Middleware CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints untuk Smart Filters
@app.get('/nn/saf')
def saf(payload: str):
    return smart_applicant_filter(payload)

@app.get('/nn/sjf')
def sjf(payload: str):
    return smart_job_filter(payload)

@app.get('/nn/srs')
def srs(user_resume: str, job_desc: str):
    return smart_recommendation_skill(user_resume, job_desc)

# Endpoint login dan mendapatkan JWT
@app.post('/companies/login')
def login_company(email: str, password: str):
    hashed_password = hash_password(password)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM companies WHERE email = ? AND password = ?', (email, hashed_password))
        company = cursor.fetchone()
        if company:
            token = create_jwt(company[0], company[2])  # company[0] = company_id, company[2] = company_name
            return {"message": "Login successful", "access_token": token}
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")

# Endpoint untuk mendapatkan data perusahaan
@app.get("/companies/me")
def get_company_data(token: str = Depends(verify_jwt)):
    company_id = token['company_id']  # Mengambil company_id dari token
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        company = cursor.fetchone()
        if company:
            return {
                "id": company[0],              # id
                "role_id": company[1],         # role_id
                "name": company[2],            # name
                "email": company[3],           # email
                "phone_number": company[4],    # phone_number
            }
        else:
            raise HTTPException(status_code=404, detail="Company not found")

# Endpoint untuk mendaftar perusahaan
@app.post('/companies/register')
def register_company(email: str, password: str, company_name: str, phone_number: str):
    hashed_password = hash_password(password)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO companies (email, password, name, phone_number, role_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, hashed_password, company_name, phone_number, 1))
            conn.commit()
        return {"message": "Company registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")

# Endpoint untuk mendapatkan daftar pekerjaan
@app.get('/job-vacancies')
def job_vacancies():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_vacancies JOIN companies ON job_vacancies.company_id = companies.id')
        data = cursor.fetchall()
        outs = []
        for d in data:
            out = {
                'id': d[0],
                'company_id': d[1],
                'name': d[2],
                'description': d[3],
                'requirement': d[4],
                'created_at': d[5],
                'updated_at': d[6],
                'company': {
                    'id': d[7],
                    'user_id': d[8],
                    'created_at': d[11],
                    'updated_at': d[12],
                },
            }
            outs.append(out)
        return outs
    
app.include_router(jobs_router)

# Endpoint untuk melihat daftar tabel dalam database
@app.get('/tables')
def list_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in cursor.fetchall()]

