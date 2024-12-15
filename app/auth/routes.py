from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import schemas, models, hashing, jwt_handler

router = APIRouter()

@router.post("/register", response_model=schemas.TokenResponse)
def register_user(user: schemas.ApplicantCreate, db: Session = Depends(get_db)):
    if db.query(models.Applicant).filter(models.Applicant.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hashing.hash_password(user.password)
    new_user = models.Applicant(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = jwt_handler.create_access_token({"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.TokenResponse)
def login_user(credentials: schemas.ApplicantLogin, db: Session = Depends(get_db)):
    user = db.query(models.Applicant).filter(models.Applicant.email == credentials.email).first()
    if not user or not hashing.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = jwt_handler.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
