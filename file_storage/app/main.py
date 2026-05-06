from fastapi import FastAPI
from .database import engine, Base
from .routers import files

Base.metadata.create_all(bind=engine)

app = FastAPI(title="File Storage Service")
app.include_router(files.router, prefix="/files", tags=["files"])
