from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    token = Column(String(200), nullable=True)

    # Отношения
    created_tasks = relationship("Task", back_populates="author")  # Задачи, созданные пользователем
    assigned_tasks = relationship(
        "Task",
        secondary="task_user_association",  # Указание на ассоциативную таблицу
        back_populates="assigned_users"
    )

    def __repr__(self):
        return f"<User {self.username}>"
