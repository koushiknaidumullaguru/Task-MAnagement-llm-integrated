from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))

    tasks = relationship("Tasks", back_populates="user")

class Tasks(Base):
    __tablename__ =  "TODO"
    id = Column(Integer, primary_key = True, autoincrement=True)
    activity = Column(String(255), nullable=False)
    Time_Created =Column(DateTime, default = func.now())
    Status = Column(String(255), nullable=False)
    isExisted = Column(Boolean, nullable = False, default = True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    user = relationship("User", back_populates="tasks")
    