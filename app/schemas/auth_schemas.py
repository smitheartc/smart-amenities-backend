# app/schemas/auth_schemas.py
from pydantic import BaseModel, EmailStr

class UserSignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"