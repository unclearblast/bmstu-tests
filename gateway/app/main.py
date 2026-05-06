from fastapi import FastAPI
from .routers import works

app = FastAPI(title="CosmoScan Gateway")
app.include_router(works.router, prefix="/works", tags=["works"])
