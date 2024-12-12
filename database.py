import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME", "job_portal.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

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
