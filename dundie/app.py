from fastapi import FastAPI
from dundie.routes.user import router as user_router

app = FastAPI(
  title="Dundie",
  description="Dundie is a rewards API.",
  version="0.1.1"
)

app.include_router(user_router, prefix="/user", tags=["user"])