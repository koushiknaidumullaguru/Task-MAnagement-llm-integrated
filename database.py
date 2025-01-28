from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL ="mysql+mysqlconnector://root:root%40123@localhost:3306/demo"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Session local for database access
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)