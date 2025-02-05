from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# User Schema
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str
    # created_by: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role : str
    created_by : int

    class config:
        orm_mode = True

# Task Schema
class TaskCreate(BaseModel):
    activity: str
    Status: str
    user_id: int
    isExisted: Optional[bool] = True

class TaskResponse(BaseModel):
    id: int
    activity: str
    Time_Created: datetime
    Status: str
    isExisted: bool
    user_id: int

    class config:
        orm_mode = True

#USER-TASK

class UserTaskResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    tasks: List[TaskResponse]


class UserLogin(BaseModel):
    email: EmailStr
    password : str