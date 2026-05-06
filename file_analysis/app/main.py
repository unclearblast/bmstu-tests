from fastapi import FastAPI
from .database import engine, Base
from .routers import analysis, wordcloud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="File Analysis Service")
app.include_router(analysis.router)
app.include_router(wordcloud.router)
