from sqlalchemy import Column, Integer, String, DateTime,Date,Boolean
from datetime import datetime, timezone
from sqlalchemy.sql import func
from database import Base, engine
from time_utils import now_ist

class TokenUsage(Base):
    __tablename__ = "token_usage"

    token = Column(String(100), primary_key=True, index=True)
    used = Column(Boolean, default=False)
    used_at = Column(DateTime, default=None)

class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Reg_No = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), unique=True)
    password = Column(String(255), unique=True)
    Role = Column(String(100))
    created_date = Column(DateTime, default=now_ist)
    last_login = Column(DateTime, default=None)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    Reg_No = Column(String(100), unique=True, nullable=False)
    First_name = Column(String(100), nullable=False)
    Last_name = Column(String(100), nullable=False)
    DOB = Column(Date, nullable=False)
    Gender = Column(String(100), nullable=False)
    Father_name = Column(String(100), nullable=False)
    Mother_name = Column(String(100), nullable=False)
    Address = Column(String(255), nullable=False)
    Phone_No = Column(String(100), nullable=False)
    Class = Column(String(100), nullable=False)
    Section = Column(String(100), nullable=False)
    Clas_sec = Column(String(100), nullable=False)
    Category = Column(String(100), nullable=False)
    created_date = Column(DateTime, default=now_ist)

# Create the table(s)
Base.metadata.create_all(bind=engine)