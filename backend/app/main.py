from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.app.routers.tasks import router as tasks_router
##from backend.app.routers.users import router as users_router
from backend.app.routers.auth import router as auth_router
from backend.app.database import engine, Base

app = FastAPI()

# Подключение роутеров
app.include_router(tasks_router)
##app.include_router(users_router)
app.include_router(auth_router)


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
