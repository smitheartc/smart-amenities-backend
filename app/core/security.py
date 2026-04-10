# app/core/security.py
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import os
from dotenv import load_dotenv


# Secret key used to sign the tokens. 
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

def hash_password(password: str) -> str:
    # 1. Convert string to bytes
    pwd_bytes = password.encode('utf-8')
    # 2. Generate a random salt
    salt = bcrypt.gensalt()
    # 3. Hash the password
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    # 4. Return as a string so it can be saved in the database
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Convert both strings back to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    # Check if they match
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt