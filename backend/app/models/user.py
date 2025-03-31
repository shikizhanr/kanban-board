from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users" 
    
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    token = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"