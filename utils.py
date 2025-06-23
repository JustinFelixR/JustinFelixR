from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta,timezone
from model import User
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from time_utils import now_ist

load_dotenv()  # Load environment variables from .env file

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_value(value: str) -> str:
    return pwd_context.hash(value)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def is_password_duplicate(db: Session, plain_password: str) -> bool:
    users = db.query(User).all()
    for user in users:
        if verify_password(plain_password, user.password):
            return True
    return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = now_ist()+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return payload  # includes role, sub, etc.
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

