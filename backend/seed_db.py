import sys
import os

# Добавляем путь к папке app в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app import User, Task, TaskStatus  # Абсолютный импорт
from backend.app import Base  # Абсолютный импорт


def seed_data():
    # Конфигурация подключения (замените на свои данные)
    DATABASE_URL = "postgresql://postgres:2gGUhN05@localhost/postgres"

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Очистка таблиц (только для тестов!)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        # Добавление пользователей
        user1 = User(first_name="Иван", last_name="Петров")
        user2 = User(first_name="Мария", last_name="Сидорова")
        user3 = User(first_name="Евгения", last_name="Иванова")
        user4 = User(first_name="Александр", last_name="Пульдас")
        session.add_all([user1, user2])
        session.commit()

        # Добавление задач
        task1 = Task(
            title="Разработать API",
            description="Создать эндпоинты для задач",
            task_type="Разработка",
            status=TaskStatus.IN_PROGRESS,
            author_id=user1.id
        )

        task2 = Task(
            title="Тестирование",
            description="Написать unit-тесты",
            task_type="Тестирование",
            status=TaskStatus.PLANNED,
            author_id=user2.id
        )

        task3 = Task(
            title="Исправление бага",
            description="Исправить ошибку, из-за которой пользователь не может авторизироваться",
            task_type="Исправление",
            status=TaskStatus.PLANNED,
            author_id=user2.id
        )

        task1.assigned_users.extend([user1, user2])
        task2.assigned_users.append(user2)
        task3.assigned_users.extend([user3, user4])

        session.add_all([task1, task2, task3])
        session.commit()

        print("✅ Тестовые данные успешно добавлены!")

    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()