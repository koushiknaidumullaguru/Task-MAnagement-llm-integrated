from fastapi import FastAPI
from apis.users import router as user_router
from models.users import Base
from database import engine

# Initialize FastAPI app
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(user_router)

# Middleware (optional)
@app.middleware("http")
async def add_custom_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Custom-Header"] = "CustomValue"
    return response

# Run the app: `uvicorn main:app --reload`
