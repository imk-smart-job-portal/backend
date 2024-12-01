import jwt
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY, ALGORITHM

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)  # Token berlaku selama 1 jam
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
