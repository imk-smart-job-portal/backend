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
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        # Tabel roles
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
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
            required_skills TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )''')
        conn.commit()
