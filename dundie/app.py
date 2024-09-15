from fastapi import FastAPI, HTTPException
from .routes import main_router

app = FastAPI(
  title="Dundie",
  description="Dundie is a rewards API.",
  version="0.1.1"
)

app.include_router(main_router)