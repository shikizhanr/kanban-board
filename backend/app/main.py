from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Import StaticFiles
import os
from contextlib import asynccontextmanager

from app.api.routers import router as api_router
from app.db.session import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения.
    """
    print("Application startup...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables checked/created.")
    yield
    print("Application shutdown.")

app = FastAPI(title="Kanban Board API", lifespan=lifespan)

# Список доменов, с которых разрешены запросы.
# Для разработки мы разрешаем адрес, на котором работает Vite.
origins = [
    "http://localhost",
    "http://localhost:5173", # Адрес вашего фронтенда
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Разрешаем все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"], # Разрешаем все заголовки
)

# Define the uploads directory for main.py context
UPLOADS_DIR_MAIN = "uploads" 
# Ensure the directory exists (though routers.py also does this, belt and suspenders)
os.makedirs(UPLOADS_DIR_MAIN, exist_ok=True) 

# Mount static files for uploads - this path should now be /api/uploads
app.mount("/api/uploads", StaticFiles(directory=UPLOADS_DIR_MAIN), name="api_uploads")



app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Kanban Board API"}