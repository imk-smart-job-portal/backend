from sqlalchemy import Column, Integer, String
from app.database import Base

class Applicant(Base):
    __tablename__ = "applicants"  # Nama tabel di database
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)