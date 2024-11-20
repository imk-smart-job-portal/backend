import json
import os
import sqlite3
# from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from unsloth import FastLanguageModel

conn = sqlite3.connect("awdaydb.db")  # Pastikan file database ada di direktori yang sesuai
conn.row_factory = sqlite3.Row  # Untuk mengembalikan data sebagai objek seperti dict

app = FastAPI()

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
# You are a summarizer system that produces required skills based on the job description provided, the output must be a JSON object that has the keys `required_skills` array of strings. Don't add "json```" string. Don't provide an explanation, it just has to be JSON, please.
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
# You are a system that extracts required skills from the resume provided by the user. The output must be a JSON object with a single key "required_skills", containing an array of unique strings. Ensure that the output is strictly in JSON format without any additional code formatting like "```json". Do not duplicate any skills.
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
    with sqlite3.connect("awdaydb.db") as conn:
        cursor = conn.cursor()
        # Tabel perusahaan
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            about TEXT,
            location TEXT,
            created_at TEXT,
            updated_at TEXT
        )''')
        # Tabel lowongan kerja
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            name TEXT,
            description TEXT,
            requirement TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )''')
        conn.commit()

# Inisialisasi database
initialize_database()