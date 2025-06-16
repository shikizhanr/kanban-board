from fastapi import FastAPI
from app.api.routers import router as api_router
from app.db.session import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения.
    Код до yield выполняется при старте.
    Код после yield - при остановке.
    """
    print("Application startup...")
    async with engine.begin() as conn:
        # В реальном проекте миграции лучше делать через Alembic,
        # а эту строку закомментировать. Для простоты оставляем.
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables checked/created.")
    yield
    print("Application shutdown.")

# Создаем приложение с новым обработчиком lifespan
app = FastAPI(title="Kanban Board API", lifespan=lifespan)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Kanban Board API"}