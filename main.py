import json
import os
import sqlite3
# from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
# from unsloth import FastLanguageModel
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt as pyjwt
from datetime import datetime, timedelta
from fastapi import File, UploadFile
from PyPDF2 import PdfReader
from docx import Document
import json
from io import BytesIO


##conn = sqlite3.connect("awdaydb.db")  # Pastikan file database ada di direktori yang sesuai
##conn.row_factory = sqlite3.Row  # Untuk mengembalikan data sebagai objek seperti dict

DATABASE = "job_portal.db"
conn = sqlite3.connect(DATABASE, check_same_thread=False)
conn.row_factory = sqlite3.Row

SECRET_KEY = "your-secret-key"  # Ganti dengan secret key Anda
ALGORITHM = "HS256"

#Helper Ekstrasi
def extract_text_from_pdf(file_content: bytes) -> str:
    """Ekstrak teks dari file PDF."""
    pdf_reader = PdfReader(BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text.strip()

def extract_text_from_docx(file_content: bytes) -> str:
    """Ekstrak teks dari file DOCX."""
    doc = Document(BytesIO(file_content))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text.strip()

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
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Endpoints register
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
#endpoint login
@app.post("/login", response_model=TokenResponse)
def login_user(credentials: LoginRequest):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants WHERE email = ?", (credentials.email,))
    user = cursor.fetchone()
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = create_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

#endpoint upload resume
@app.post("/upload-resume")
async def upload_resume(applicant_id: int, file: UploadFile = File(...)):
    # Validasi format file
    if file.content_type == "application/pdf":
        # Baca teks dari file PDF
        reader = PdfReader(file.file)
        text = " ".join([page.extract_text() for page in reader.pages])
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # Baca teks dari file DOCX
        doc = Document(file.file)
        text = " ".join([p.text for p in doc.paragraphs])
    else:
        # Jika format file tidak valid
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Konversi teks mentah ke JSON terstruktur (contoh sederhana)
    parsed_json = {
        "applicant_id": applicant_id,
        "raw_text": text,
        "name": None,  # Ekstraksi nama (gunakan regex atau NLP di masa depan)
        "email": None,  # Ekstraksi email
        "skills": [],   # Ekstraksi skill
        "education": None,  # Ekstraksi pendidikan
        "experience": None  # Ekstraksi pengalaman kerja
    }

    # Ubah JSON menjadi string sebelum disimpan
    json_string = json.dumps(parsed_json)

    # Simpan string JSON ke database
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO resumes (applicant_id, files) VALUES (?, ?)",
        (applicant_id, json_string)
    )
    conn.commit()

    return {"message": "Resume uploaded and processed successfully"}

#Endpoint cek resume
@app.get("/resume/{applicant_id}")
def get_resume(applicant_id: int):
    cursor = conn.cursor()
    cursor.execute("SELECT files FROM resumes WHERE applicant_id = ?", (applicant_id,))
    result = cursor.fetchone()
    if result:
        # Ubah string JSON kembali ke objek JSON
        resume_json = json.loads(result["files"])
        return resume_json
    raise HTTPException(status_code=404, detail="Resume not found")

@app.put("/resume/{resume_id}")
async def update_resume(resume_id: int, file: UploadFile = File(...)):
    # Cek apakah resume dengan resume_id ada
    cursor = conn.cursor()
    cursor.execute("SELECT applicant_id FROM resumes WHERE id = ?", (resume_id,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Resume not found")

    applicant_id = result[0]  # Ambil applicant_id dari database

    # Validasi format file
    if file.content_type == "application/pdf":
        # Baca teks dari file PDF
        reader = PdfReader(file.file)
        text = " ".join([page.extract_text() for page in reader.pages])
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # Baca teks dari file DOCX
        doc = Document(file.file)
        text = " ".join([p.text for p in doc.paragraphs])
    else:
        # Jika format file tidak valid
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Konversi teks mentah ke JSON terstruktur (contoh sederhana)
    parsed_json = {
        "applicant_id": applicant_id,
        "raw_text": text,
        "name": None,  # Ekstraksi nama (gunakan regex atau NLP di masa depan)
        "email": None,  # Ekstraksi email
        "skills": [],   # Ekstraksi skill
        "education": None,  # Ekstraksi pendidikan
        "experience": None  # Ekstraksi pengalaman kerja
    }

    # Ubah JSON menjadi string sebelum disimpan
    json_string = json.dumps(parsed_json)

    # Update resume di database
    cursor.execute(
        "UPDATE resumes SET files = ? WHERE id = ?",
        (json_string, resume_id)
    )
    conn.commit()

    return {"message": "Resume updated successfully"}

#endpoint delete resume
@app.delete("/resume/{resume_id}")
def delete_resume(resume_id: int):
    # Cek apakah resume ada di database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    resume = cursor.fetchone()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Hapus resume dari database
    cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
    conn.commit()

    return {"message": "Resume deleted successfully"}


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

SECRET_KEY = "your-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Fungsi untuk membuat JWT token
def create_jwt(company_id: int, company_name: str):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "company_id": company_id,
        "company_name": company_name,
        "exp": expiration_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Fungsi untuk memverifikasi JWT token
def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# model, tokenizer = FastLanguageModel.from_pretrained(
#     model_name='estradax/awday-llm-v2',
#     max_seq_length=max_seq_length,
#     dtype=dtype,
#     load_in_4bit=load_in_4bit,
# )

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

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

# Endpoint untuk login dan mendapatkan token JWT
@app.post('/companies/login')
def login_company(email: str, password: str):
    hashed_password = hash_password(password)
    with sqlite3.connect("awdaydb.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM companies WHERE email = ? AND password = ?
        ''', (email, hashed_password))
        company = cursor.fetchone()
        if company:
            # Membuat token JWT
            token = create_jwt(company[0], company[2])  # company[0] = company_id, company[2] = company_name
            return {"message": "Login successful", "access_token": token}
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")

# Endpoint untuk mendapatkan data perusahaan yang login (memerlukan JWT)
@app.get("/companies/me")
def get_company_data(token: str = Depends(verify_jwt)):
    company_id = token['company_id']
    with sqlite3.connect("awdaydb.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        company = cursor.fetchone()
        if company:
            return {
                "id": company[0],
                "email": company[1],
                "name": company[2],
                "about": company[3],
                "location": company[4],
                "phone_number": company[5],
            }
        else:
            raise HTTPException(status_code=404, detail="Company not found")

# Endpoint untuk mendaftar perusahaan
@app.post('/companies/register')
def register_company(email: str, password: str, about: str, location: str, company_name: str, phone_number: str):
    hashed_password = hash_password(password)
    try:
        with sqlite3.connect("awdaydb.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO companies (email, password, about, location, name, phone_number, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            ''', (email, hashed_password, about, location, company_name, phone_number))
            conn.commit()
        return {"message": "Company registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")

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


def get_db():
    conn = sqlite3.connect("job_portal.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Endpoint untuk mendapatkan daftar tabel dalam database SQLite
@app.get('/tables')
def list_tables(db: sqlite3.Connection = Depends(get_db)):
    q = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = conn.execute(q).fetchall()
    return [table['name'] for table in tables]

@app.get('/tables/companies')
def inspect_table_companies(db: sqlite3.Connection = Depends(get_db)):
    q = "PRAGMA table_info(companies);"
    columns = db.execute(q).fetchall()
    return [{"id": col[0], "name": col[1], "type": col[2]} for col in columns]

@app.get('/companies/all')
def list_companies(db: sqlite3.Connection = Depends(get_db)):
    q = "SELECT * FROM companies;"
    companies = db.execute(q).fetchall()
    return [dict(company) for company in companies]

@app.get('/tables/inspect/{table_name}')
def inspect_table(table_name: str, db: sqlite3.Connection = Depends(get_db)):
    q = f"PRAGMA table_info({table_name});"
    columns = db.execute(q).fetchall()
    return [{"id": col[0], "name": col[1], "type": col[2]} for col in columns]

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