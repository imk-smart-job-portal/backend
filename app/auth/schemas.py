from pydantic import BaseModel, EmailStr

# Input untuk register
class ApplicantCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# Input untuk login
class ApplicantLogin(BaseModel):
    email: EmailStr
    password: str

# Output untuk token JWT
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
