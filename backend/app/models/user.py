from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

# Отношения
    created_tasks = relationship("Task", back_populates="author")  # Задачи, созданные пользователем
    assigned_tasks = relationship(
        "Task",
        secondary="task_user_association",  # Указание на ассоциативную таблицу
        back_populates="assigned_users"
    )

    def repr(self):
        return f"<User {self.username}>"