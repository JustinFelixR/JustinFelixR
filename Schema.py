from typing import List
from pydantic import BaseModel, constr, field_validator,SecretStr,Field
import re
from typing import List
from model import Base
from datetime import datetime,date
from typing import Optional



class RegNoLoginRequest(BaseModel):
    reg_no: str
    password: SecretStr




class Users(BaseModel):
    Reg_No: str = Field(..., example="STU2025A001")
    name: str = Field(..., example="admin_user")
    password: SecretStr = Field(..., example="StrongP@ssw0rd")
    Role: str = Field(..., example="admin")

    model_config = {
        "from_attributes": True
    }

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        plain = value.get_secret_value()

        if len(plain) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", plain):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", plain):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", plain):  # ✅ Accept digits 0–9 only
            raise ValueError("Password must contain at least one digit (0–9)")
        if not re.search(r"[^\w\s]", plain):  # ✅ Special characters only (not alphanumeric or underscore)
            raise ValueError("Password must contain at least one special character")

        return value

    

class UserOut(BaseModel):
    id: int
    Reg_No : str
    name: str
    Role: str
    created_date: datetime

    model_config = {
        "from_attributes": True
    }


class BulkUserRequest(BaseModel):
    users: List[Users]


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StudentSchema(BaseModel):
    Reg_No: str = Field(..., example="STU2025A001")
    First_name: str = Field(..., example="Alice")
    Last_name: str = Field(..., example="Johnson")
    DOB: date = Field(..., example="2010-05-15")
    Gender: str = Field(..., example="Female")
    Father_name: str = Field(..., example="Robert Johnson")
    Mother_name: str = Field(..., example="Emily Johnson")
    Address: str = Field(..., example="123 Main Street, Bangalore")
    Phone_No: str = Field(..., example="9876543210")
    Class: str = Field(..., example="8")
    Section: str = Field(..., example="A")
    Category: str = Field(..., example="General")

    model_config = {
       "from_attributes": True
    }

