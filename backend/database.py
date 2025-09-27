from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy import PrimaryKeyConstraint

# Настройки подключения к базе данных
DATABASE_URL = "postgresql://get4ar:1532@localhost:5432/postgres"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Base class for models
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Students(Base):
    __tablename__ = "students"

    last_name = Column(String)
    first_name = Column(String)
    patronymic = Column(String)
    study_year = Column(Integer)
    group_name = Column(String)
    faculty_name = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint('last_name', 'first_name', 'patronymic'),
    )