import json
import os
import sqlite3
# from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
# from unsloth import FastLanguageModel
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

##conn = sqlite3.connect("awdaydb.db")  # Pastikan file database ada di direktori yang sesuai
##conn.row_factory = sqlite3.Row  # Untuk mengembalikan data sebagai objek seperti dict

DATABASE = "job_portal.db"
conn = sqlite3.connect(DATABASE, check_same_thread=False)
conn.row_factory = sqlite3.Row

SECRET_KEY = "your-secret-key"  # Ganti dengan secret key Anda
ALGORITHM = "HS256"

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class RegisterRequest(BaseModel):
    role_id: int
    name: str
    email: str
    phone_number: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Helper Functions
def create_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Endpoints
@app.post("/register", response_model=TokenResponse)
def register_user(user: RegisterRequest):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants WHERE email = ?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    cursor.execute("""
        INSERT INTO applicants (role_id, name, email, phone_number, password)
        VALUES (?, ?, ?, ?, ?)
    """, (user.role_id, user.name, user.email, user.phone_number, hashed_password))
    conn.commit()
    
    token = create_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=TokenResponse)
def login_user(credentials: LoginRequest):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants WHERE email = ?", (credentials.email,))
    user = cursor.fetchone()
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = create_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

# Middleware untuk mengizinkan akses dari berbagai sumber (CORS)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

max_seq_length = 2048 
dtype = None
load_in_4bit = True

# model, tokenizer = FastLanguageModel.from_pretrained(
#     model_name='estradax/awday-llm-v2',
#     max_seq_length=max_seq_length,
#     dtype=dtype,
#     load_in_4bit=load_in_4bit,
# )

def smart_applicant_filter(payload: str):
#     system_prompt = """
# You are a summarizer system that produces required skills based on the job description provided, the output must be a JSON object that has the keys required_skills array of strings. Don't add "json" string. Don't provide an explanation, it just has to be JSON, please.
# 
# """
#     user_prompt = """
# # Job Description
# {}
# """.format(payload)
# 
#     messages = [
#             {'role': 'system', 'content': system_prompt},
#             {'role': 'user', 'content': user_prompt}
#     ]
# 
#     inputs = tokenizer(
#     [
#       tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
#     ], return_tensors="pt", add_special_tokens=False).to("cuda")
# 
#     outputs = model.generate(**inputs, use_cache=True, max_new_tokens=1024)
#     outputs_str = tokenizer.batch_decode(outputs[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]
# 
#     return json.loads(outputs_str)
    pass

def smart_job_filter(payload: str):
#     system_prompt = """
# You are a system that extracts required skills from the resume provided by the user. The output must be a JSON object with a single key "required_skills", containing an array of unique strings. Ensure that the output is strictly in JSON format without any additional code formatting like "json". Do not duplicate any skills.
# """
#     user_prompt = """
# # User Data 
# {}
# """.format(payload)
# 
#     messages = [
#             {'role': 'system', 'content': system_prompt},
#             {'role': 'user', 'content': user_prompt}
#     ]
# 
#     inputs = tokenizer(
#     [
#       tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
#     ], return_tensors="pt", add_special_tokens=False).to("cuda")
# 
#     outputs = model.generate(**inputs, use_cache=True, max_new_tokens=1024)
#     outputs_str = tokenizer.batch_decode(outputs[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]
# 
#     return json.loads(outputs_str)
    pass

def smart_recommendation_skill(user_resume: str, job_desc: str):
#     system_prompt = """Analyze a given user resume and job description to identify key skills and requirements. Based on this analysis, generate a list of recommended skills that the candidate should consider developing or acquiring to increase their chances of securing the job. Prioritize recommendations based on the job's specific requirements and the candidate's current skill set. Output the results in a JSON format with a key named "recommended_skills" containing a list of strings representing the recommended skills."""
#
#     user_prompt = """# User Resume
# {}
#
# Job Description
# {}
# 
# Output:
# """.format(user_resume, job_desc)
# 
#     messages = [
#             {'role': 'system', 'content': system_prompt},
#             {'role': 'user', 'content': user_prompt}
#     ]
# 
#     inputs = tokenizer(
#     [
#       tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
#     ], return_tensors="pt", add_special_tokens=False).to("cuda")
# 
#     outputs = model.generate(**inputs, use_cache=True, max_new_tokens=1024)
#     outputs_str = tokenizer.batch_decode(outputs[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]
# 
#     return json.loads(outputs_str)
    pass

# Smart Applicant Filter
@app.get('/nn/saf')
def saf(payload: str):
    return smart_applicant_filter(payload)

# Smart Job Filter
@app.get('/nn/sjf')
def sjf(payload: str):
    return smart_job_filter(payload)

# Smart Recommendation Skill
@app.get('/nn/srs')
def srs(user_resume: str, job_desc: str):
    return smart_recommendation_skill(user_resume, job_desc)

@app.get('/job-vacancies')
def job_vacancies():
    q = 'SELECT * FROM job_vacancies JOIN companies ON job_vacancies.company_id = companies.id'
    data = conn.execute(q).fetchall()
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
                'about': d[9],
                'location': d[10],
                'created_at': d[11],
                'updated_at': d[12],
            },
        }
        outs.append(out)

    return outs 

# Endpoint untuk mendapatkan daftar tabel dalam database SQLite
@app.get('/tables')
def list_tables():
    q = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = conn.execute(q).fetchall()
    return [table['name'] for table in tables]

# Skrip untuk membuat database jika belum ada
def initialize_database():
    with sqlite3.connect("job_portal.db") as conn:
        cursor = conn.cursor()
         # Tabel roles
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )''')

        # Tabel applicants
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone_number TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY (role_id) REFERENCES roles (id)
        )''')

        # Tabel companies
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone_number TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY (role_id) REFERENCES roles (id)
        )''')

        # Tabel categories
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )''')

        # Tabel jobs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            category_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            experience_level TEXT,
            education_level TEXT,
            career_level TEXT,
            employment_type TEXT,
            required_skills TEXT, -- JSON format
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )''')

        # Tabel resumes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_id INTEGER NOT NULL,
            files TEXT NOT NULL,
            FOREIGN KEY (applicant_id) REFERENCES applicants (id)
        )''')

        # Tabel job_applications
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            application_date TEXT NOT NULL,
            application_status TEXT,
            similarity_score REAL, -- Nilai cosine similarity
            FOREIGN KEY (applicant_id) REFERENCES applicants (id),
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        )''')

        conn.commit()

# Inisialisasi database
initialize_database()