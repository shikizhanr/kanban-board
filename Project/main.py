from fastapi import FastAPI
from routes.auth import auth_router  # Импортируем auth_router

app = FastAPI()

# Подключение маршрутов
app.include_router(auth_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}