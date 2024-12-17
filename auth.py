import hashlib
import jwt
import datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
import os
# from jwt import decode as jwt_decode, ExpiredSignatureError, InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password_hashlib(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt(sub: str, company_id: int):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "company_id": company_id,
        "sub": sub,
        "exp": expiration_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         # Decode the JWT Token
#         payload = jwt_decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         applicant_id = payload.get("id")
#         if not applicant_id:
#             raise HTTPException(
#                 status_code=401,
#                 detail="Invalid token: missing applicant_id",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         return int(applicant_id)  # Ensure applicant_id is an integer
#     except ExpiredSignatureError:
#         raise HTTPException(
#             status_code=401,
#             detail="Token has expired",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except InvalidTokenError:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
