from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import PaginatedResponse, StudentOut
from database import get_db, Base, engine, Students
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Создание таблиц БД
Base.metadata.create_all(bind=engine)

# Настройка CORS для фронта
origins = [
    'http://127.127.127.127',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Основная страница
@app.get("/students/", response_model=PaginatedResponse)
def get_students(page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    # Проверка, чтобы страница и размер были положительными
    if page < 1 or size < 1:
        return {"error": "Page and size parameters must be positive integers."}

    # Расчет offset
    offset = (page - 1) * size

    try:
        # Запрос к БД для получения студентов
        students_query = db.query(Students).offset(offset).limit(size).all()

        # Подсчет общего количества студентов
        total_students = db.query(Students).count()

        # Вычисление общего количества страниц
        total_pages = (total_students // size) + (1 if total_students % size > 0 else 0)

        # Преобразование объектов ORM в Pydantic
        student_outs = [StudentOut.from_orm(student) for student in students_query]

        return PaginatedResponse(
            students=student_outs,
            totalPages=total_pages
        )
    
    except SQLAlchemyError as e:
        return {"error": str(e)}

# Создание записей в БД
@app.post("/students/create/")
def post_students(student: StudentOut, db: Session = Depends(get_db)):
    if db.query(Students).filter(Students.last_name == student.last_name,
                                 Students.first_name == student.first_name,
                                 Students.patronymic == student.patronymic).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this name is already exists."
        )
    
    db_input = Students(**student.dict())

    db.add(db_input)
    db.commit()
    db.refresh(db_input)
    
    return db_input

# Удаление записей из бд
@app.delete("/students/delete/")
def delete_students(student: StudentOut, db: Session = Depends(get_db)):
    db_student = db.query(Students).filter(
        Students.last_name == student.last_name,
        Students.first_name == student.first_name,
        Students.patronymic == student.patronymic
    ).first()

    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this name does not exist."
        )
    
    db.delete(db_student)
    db.commit()
    
    return db_student
