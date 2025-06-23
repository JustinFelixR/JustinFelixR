from fastapi import FastAPI, Depends, HTTPException, status,Query
from fastapi.security import OAuth2PasswordRequestForm
from model import User, Base,TokenUsage
from Schema import Users, UserOut, BulkUserRequest,RegNoLoginRequest
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from utils import hash_password, is_password_duplicate,create_access_token,verify_password,get_current_user
from Routers import Student_Upload
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
from time_utils import now_ist

#load_dotenv()
load_dotenv(override=True)

#-----------------------------------------------------------------------------------------------------
#Single time token initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    token_value = os.getenv("ONE_TIME_USER_TOKEN")
    if token_value:
        db: Session = SessionLocal()
        if not db.query(TokenUsage).filter_by(token=token_value).first():
            db_token = TokenUsage(token=token_value, used=False)
            db.add(db_token)
            db.commit()
        db.close()

    yield 

#-------------------------------------------------------------------------------------------------
app = FastAPI(
    title="School ERP System",
    description="API for managing school operations including student data upload",
    version="1.0.0",
    lifespan=lifespan
)


# Dependency: get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#-----------------------------------------------------------------------------------------------------

@app.post("/addoneuser", response_model=UserOut)
async def add_user(
    request: Users,
    token: str = Query(..., description="One-time-use access token"),
    db: Session = Depends(get_db)
):
    db_token = db.query(TokenUsage).filter_by(token=token).first()
    if not db_token or db_token.used:
        raise HTTPException(status_code=403, detail="Invalid or expired token.")

    # Invalidate token
    db_token.used = True
    db_token.used_at = now_ist()
    db.commit()

    if db.query(User).filter(User.Reg_No == request.Reg_No).first():
        raise HTTPException(status_code=400, detail="Registration number already exists")


    plain_password = request.password.get_secret_value()

    if is_password_duplicate(db, plain_password):
        raise HTTPException(
            status_code=409,
            detail="Password already in use. Please choose a different one."
        )

    hashed_pw = hash_password(plain_password)

    user = User(
        Reg_No=request.Reg_No,
        name=request.name,
        password=hashed_pw,
        Role=request.Role,
        created_date=now_ist()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user
#---------------------------------------------------------------------------------------------------------------------
@app.post("/adduser", response_model=UserOut)
async def add_user(request: Users, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "principle"]:
        raise HTTPException(status_code=403, detail="You do not have permission to add users.")
    if db.query(User).filter(User.name == request.name).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.Reg_No == request.Reg_No).first():
        raise HTTPException(status_code=400, detail="Registration number already exists")

    plain_password = request.password.get_secret_value()

    if is_password_duplicate(db, plain_password):
        raise HTTPException(
            status_code=409,
            detail="Password already in use. Please choose a different one."
        )

    hashed_pw = hash_password(plain_password)

    user = User(
        Reg_No=request.Reg_No,
        name=request.name,
        password=hashed_pw,
        Role=request.Role,
        created_date=now_ist()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user  # Sanitized via UserOut
#---------------------------------------------------------------------------------------------------------------------
@app.post("/addusers", status_code=status.HTTP_207_MULTI_STATUS)
async def bulk_add_users(
    request: BulkUserRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["admin", "principle"]:
        raise HTTPException(status_code=403, detail="You do not have permission to add users.")

    results = []

    for user_data in request.users:
        reg_no = user_data.Reg_No
        role = user_data.Role
        name = user_data.name
        plain_password = user_data.password.get_secret_value()
        issues = []

        # 🔁 Check for duplicate Reg_No instead of username
        if db.query(User).filter(User.Reg_No == reg_no).first():
            issues.append("Registration number already exists")

        if issues:
            results.append({
                "reg_no": reg_no,
                "status": "failed",
                "reason": issues
            })
            continue

        hashed_pw = hash_password(plain_password)
        user = User(
            Reg_No=reg_no,
            name=name,
            password=hashed_pw,
            Role=role,
            created_date=now_ist()
        )
        db.add(user)
        db.flush()

        results.append({
            "reg_no": reg_no,
            "status": "success"
        })

    db.commit()
    return {"summary": results}
#---------------------------------------------------------------------------------------------------------------------

@app.post("/Login")
async def login(request: RegNoLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.Reg_No == request.reg_no).first()

    if not user or not verify_password(request.password.get_secret_value(), user.password):
        raise HTTPException(status_code=401, detail="Invalid Reg. No or password")

    user.last_login = now_ist()
    db.commit()

    access_token = create_access_token(data={"sub": user.Reg_No, "role": user.Role})
    return {"access_token": access_token, "token_type": "bearer"}

#---------------------------------------------------------------------------------------------
@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Map 'username' field to 'Reg_No'
    user = db.query(User).filter(User.Reg_No == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Reg. No or password")

    user.last_login = now_ist()

    db.commit()

    access_token = create_access_token(data={"sub": user.Reg_No, "role": user.Role})

    return {"access_token": access_token, "token_type": "bearer"}
#--------------------------------------------------------------------------------------------------

#Upload Student detail CSV
app.include_router(Student_Upload.router, prefix="/students", tags=["Student Upload"])
