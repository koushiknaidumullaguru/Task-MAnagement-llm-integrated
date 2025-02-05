from fastapi import HTTPException, Depends, APIRouter, Query, Body
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from models.users import Base, User, Tasks
from schemas.users import UserCreate, UserResponse, TaskCreate, TaskResponse, UserTaskResponse, UserLogin
from typing import List
from sqlalchemy import select, join, update, text
from sqlalchemy.exc import SQLAlchemyError
from scripts.model import get_Query
from utils.auth import create_access_token, get_current_user, is_admin

router = APIRouter()

@router.post("/login/", tags=["Authentication"])
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_new = db.query(User).filter(User.email == user.email).first()
    if not user_new or not user.password == user_new.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# User Management Routes
@router.post("/users/", response_model=UserResponse, tags=["User Management"])
def create_user(user: UserCreate, db: Session = Depends(get_db), admin = Depends(is_admin)):
    new_user = User(username=user.username, email=user.email, password=user.password, role = user.role, created_by = admin.id)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

@router.get("/users/", response_model=list[UserResponse], tags=["User Management"])
def get_users(db: Session = Depends(get_db), user_data = Depends(get_current_user)):
    return db.query(User).all()

@router.get("/users/{user_id}", response_model=UserResponse, tags=["User Management"])
def get_user(user_id: int, db: Session = Depends(get_db), user_data = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserResponse, tags=["User Management"])
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db), admin = Depends(is_admin)):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_user.username = user.username
    existing_user.email = user.email
    existing_user.password = user.password
    db.commit()
    db.refresh(existing_user)
    return existing_user

@router.delete("/users/{user_id}", response_model=dict, tags=["User Management"])
def delete_user(user_id: int, db: Session = Depends(get_db), admin = Depends(is_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# Task Management Routes
@router.get("/tasks/", response_model=list[TaskResponse], tags=["Task Management"])
def get_tasks(db: Session = Depends(get_db), user_data = Depends(get_current_user)):
    return db.query(Tasks).all()

@router.get("/tasks/{task_id}/", response_model=TaskResponse, tags=["Task Management"])
def get_task(task_id: int, db: Session = Depends(get_db), user_data = Depends(get_current_user)):
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks/", response_model=TaskResponse, tags=["Task Management"])
def create_task(task: TaskCreate, db: Session = Depends(get_db), admin = Depends(is_admin)):
    new_task = Tasks(activity=task.activity, Status=task.Status, user_id=task.user_id, isExisted=task.isExisted)
    db.add(new_task)
    try:
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Activity already existed")

@router.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Task Management"])
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db), admin = Depends(is_admin)):
    existing_task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    existing_task.activity = task.activity
    existing_task.Status = task.Status
    existing_task.isExisted = task.isExisted
    db.commit()
    db.refresh(existing_task)
    return existing_task

@router.delete("/tasks/{task_id}", response_model=dict, tags=["Task Management"])
def delete_task(task_id: int, db: Session = Depends(get_db), admin = Depends(is_admin)):
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.isExisted = False
    db.commit()
    return {"message": "Task successfully deleted"}

# User-Specific Tasks Routes
@router.get("/tasks_user/{user_id}", response_model=UserTaskResponse, tags=["User-Specific Tasks"])
def tasks_by_userid(user_id: int, db: Session = Depends(get_db), user_data = Depends(get_current_user)):
    stmt = select(User, Tasks).join(Tasks, User.id == Tasks.user_id).filter(User.id == user_id)
    result = db.execute(stmt).all()
    if not result:
        raise HTTPException(status_code=404, detail="User not found or no tasks available")
    user, _ = result[0]
    tasks = [task for _, task in result]
    return {"user_id": user.id, "username": user.username, "email": user.email, "tasks": tasks}

@router.delete("/task_user/{user_id}", tags=["User-Specific Tasks"])
def delete_tasks_by_userid(user_id: int, db: Session = Depends(get_db), admin = Depends(is_admin)):
    tasks = db.query(Tasks).filter(Tasks.user_id == user_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Tasks not found for given user_id")
    for task in tasks:
        task.isExisted = False
        db.commit()
    return {"message": f"{len(tasks)} tasks successfully deleted"}

@router.put("/task_user/{user_id}", tags=["User-Specific Tasks"])
def update_task_status(user_id: int, db: Session = Depends(get_db), admin = Depends(is_admin)):
    tasks = db.query(Tasks).filter(Tasks.user_id == user_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="User ID not found")
    for task in tasks:
        if task.Status == "completed":
            return {"message": "Already completed"}
        else:
            task.Status = "completed"
        db.commit()
    return {"message": "Status changed to completed"}

# SQL Query Execution Route
@router.post("/get-Query/", tags=["SQL Query Execution"])
def get_query(user_prompt: str = Body(...), db: Session = Depends(get_db), user_data = Depends(get_current_user)):
    try:
        message = get_Query(user_prompt)
        result = db.execute(text(message))
        rows = result.fetchall()
        column_names = result.keys()
        output = [dict(zip(column_names, row)) for row in rows]
        return output
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Query execution failed: {str(e)}")
