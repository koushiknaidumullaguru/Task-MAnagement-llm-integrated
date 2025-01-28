from fastapi import HTTPException, Depends,APIRouter, Query,Body
from sqlalchemy.orm import Session
from database import SessionLocal,engine
from models.users import Base, User, Tasks
from schemas.users import UserCreate, UserResponse, TaskCreate, TaskResponse, UserTaskResponse
from typing import List
from sqlalchemy import select, join, update, text
from sqlalchemy.exc import SQLAlchemyError
from scripts.model import get_Query


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(username=user.username, email=user.email, password=user.password)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")


# Read all users
@router.get("/users/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# Read a single user by ID
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Update a user
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_user.username = user.username
    existing_user.email = user.email
    existing_user.password = user.password
    db.commit()
    db.refresh(existing_user)
    return existing_user


# Delete a user
@router.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.get("/tasks/", response_model = list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Tasks).all()

@router.get("/tasks/{task_id}/", response_model =TaskResponse)
def get_task(task_id:int, db: Session = Depends(get_db)):
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail ="task not found")
    return task

@router.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Tasks(activity = task.activity, Status = task.Status,user_id = task.user_id, isExisted = task.isExisted)
    db.add(new_task)
    try:
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="activity already existed")

@router.put("/tasks/{task_id}", response_model = TaskResponse)
def update_task(task_id:int, task:TaskCreate, db:Session = Depends(get_db)):
    existing_task = db.query(Tasks).filter(Tasks.id==task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="task not found")
    existing_task.activity = task.activity
    existing_task.Status = task.Status
    existing_task.isExisted = task.isExisted
    db.commit()
    db.refresh(existing_task)
    return existing_task


@router.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id:int, db:Session = Depends(get_db)):
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    task.isExisted = False
    db.commit()
    return {"message":"task successfully deleted"}



@router.get("/tasks_user/{user_id}", response_model=UserTaskResponse)
def tasks_by_userid(user_id: int, db: Session = Depends(get_db)):
    
    stmt = (
        select(User, Tasks)
        .join(Tasks, User.id == Tasks.user_id)
        .filter(User.id == user_id)
    )

    result = db.execute(stmt).all()

    if not result:
        raise HTTPException(status_code=404, detail="User not found or no tasks available")

    user,_= result[0]  

    tasks = [task for _, task in result]


    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "tasks": tasks    
    }



@router.delete("/task_user/{user_id}")
def delete_tasks_by_userid(user_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Tasks).filter(Tasks.user_id == user_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="tasks not found for given user_id")
    for task in tasks:
        task.isExisted = False
        db.commit()
    return {"message": f"{len(tasks)} are successfully deleted"}

@router.put("/task_user/{user_id}")
def update_task(user_id:int,db:Session = Depends(get_db)):
    tasks = db.query(Tasks).filter(Tasks.user_id==user_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="user_id not found")
    for task in tasks:
        if(task.Status == "completed"):
            return {"message":"already completed"}
        else:
            task.Status = "completed"
        db.commit()
    return {"message": "status changed to completed"}



@router.post("/get-Query/")
def get_query(user_prompt: str = Body(...), db: Session = Depends(get_db)):
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