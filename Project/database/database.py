from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# ����������� � ���� ������
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:5544@localhost/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ������� ����� ��� �������
Base = declarative_base()
