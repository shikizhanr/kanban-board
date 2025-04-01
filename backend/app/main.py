from fastapi import FastAPI
from contextlib import asynccontextmanager
##from backend.app.routers.users import router as users_router
from routers.auth import router as auth_router
from routers.user import router as users_router
from database import engine, Base

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI authentication and authorization example"}


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
