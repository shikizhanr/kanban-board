from sqlalchemy import create_engine, text
from backend.app.database import Base, DATABASE_URL

engine = create_engine(DATABASE_URL)

def reset_db():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS task_user_association CASCADE"))
##        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS taskstatus CASCADE"))
        conn.commit()
    print("База данных сброшена")

if __name__ == "__main__":
    reset_db()
    Base.metadata.create_all(engine)
    print("Таблицы созданы заново")