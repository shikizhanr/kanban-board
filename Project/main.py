from fastapi import FastAPI
from routes.auth import auth_router  # ����������� auth_router

app = FastAPI()

# ����������� ���������
app.include_router(auth_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}