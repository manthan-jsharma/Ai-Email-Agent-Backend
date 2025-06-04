from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET", "dev_secret")
ALGORITHM = "HS256"

def create_jwt_token(email: str):
    expire = datetime.utcnow() + timedelta(days=1)
    payload = {
        "sub": email,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)