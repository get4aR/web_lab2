from fastapi import FastAPI, Depends, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db, Base, engine, Students
from math import ceil
from typing import Optional

app = FastAPI()

# Создание таблиц (если еще не созданы)
Base.metadata.create_all(bind=engine)

# Статические файлы и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def students_page(request: Request, page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    # Валидация
    if page < 1:
        page = 1
    if size < 1:
        size = 10

    try:
        total_students = db.query(Students).count()
    except SQLAlchemyError:
        total_students = 0

    total_pages = max(1, ceil(total_students / size))

    if page > total_pages:
        page = total_pages

    offset = (page - 1) * size
    students_query = db.query(Students).order_by(Students.last_name, Students.first_name).offset(offset).limit(size).all()

    context = {
        "request": request,
        "students": students_query,
        "current_page": page,
        "total_pages": total_pages,
        "page_size": size,
        "total_students": total_students,
    }
    return templates.TemplateResponse("students.html", context)


def _redirect_with(params: dict) -> RedirectResponse:
    """
    Вспомогательная функция для редиректа на корень с params.
    """
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = "/" + ("?" + qs if qs else "")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.post("/form/")
def handle_form(
    request: Request,
    action: str = Form(...),  # 'create' или 'delete'
    last_name: str = Form(""),
    first_name: str = Form(""),
    patronymic: str = Form(""),
    study_year: str = Form(""),
    group_name: str = Form(""),
    faculty_name: str = Form(""),
    db: Session = Depends(get_db),
):
    # Нормализация входа
    last_name = (last_name or "").strip()
    first_name = (first_name or "").strip()
    patronymic = (patronymic or "").strip()
    study_year_raw = (study_year or "").strip()
    group_name = (group_name or "").strip()
    faculty_name = (faculty_name or "").strip()

    if action == "create":
        # ВСЕ поля заполнены
        missing = []
        if not last_name:
            missing.append("last_name")
        if not first_name:
            missing.append("first_name")
        if not patronymic:
            missing.append("patronymic")
        if not study_year_raw:
            missing.append("study_year")
        if not group_name:
            missing.append("group_name")
        if not faculty_name:
            missing.append("faculty_name")

        if missing:
            return _redirect_with({"error": "missing_fields", "missing": ",".join(missing)})

        try:
            study_year_val = int(study_year_raw)
        except ValueError:
            return _redirect_with({"error": "bad_study_year"})

        # Проверка на существующего студента
        try:
            existing = db.query(Students).filter(
                Students.last_name == last_name,
                Students.first_name == first_name,
                Students.patronymic == patronymic
            ).first()
        except SQLAlchemyError:
            existing = None

        if existing:
            return _redirect_with({"error": "exists"})

        # Создаем запись
        try:
            db_obj = Students(
                last_name=last_name,
                first_name=first_name,
                patronymic=patronymic,
                study_year=study_year_val,
                group_name=group_name,
                faculty_name=faculty_name,
            )
            db.add(db_obj)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            return _redirect_with({"error": "db_error"})
        return _redirect_with({"created": "1"})

    # требуем минимум ФИО
    elif action == "delete":
        if not (last_name and first_name and patronymic):
            return _redirect_with({"error": "need_fio"})

        try:
            query = db.query(Students).filter(
                Students.last_name == last_name,
                Students.first_name == first_name,
                Students.patronymic == patronymic
            )
            if study_year_raw:
                try:
                    sy = int(study_year_raw)
                    query = query.filter(Students.study_year == sy)
                except ValueError:
                    # если год невалидный — считаем как неуказанный, но можно вернуть ошибку; выбрал игнор
                    pass
            if group_name:
                query = query.filter(Students.group_name == group_name)
            if faculty_name:
                query = query.filter(Students.faculty_name == faculty_name)

            target = query.first()
        except SQLAlchemyError:
            return _redirect_with({"error": "db_error"})

        if not target:
            return _redirect_with({"error": "notfound"})

        # Удаляем найденную запись
        try:
            db.delete(target)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            return _redirect_with({"error": "db_error"})

        return _redirect_with({"deleted": "1"})

    # Неизвестное действие
    return _redirect_with({})
