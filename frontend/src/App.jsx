import React, { useEffect, useState } from "react";
import api from './api';
import './App.css';

const App = () => {
  const [students, setStudents] = useState([]);
  const [currentPage, setCurrentPage] = useState(1); // Текущая страница
  const [totalPages, setTotalPages] = useState(1); // Общее количество страниц
  const [pageSize, setPageSize] = useState(10); // Размер страницы
  const [formData, setFormData] = useState({
    last_name: '',
    first_name: '',
    patronymic: '',
    study_year: '',
    group_name: '',
    faculty_name: ''
  });

  // Функция для получения студентов с учетом пагинации
  const fetchStudents = async () => {
    try {
      const response = await api.get('/', {
        params: {
          page: currentPage,
          size: pageSize
        }
      });
      const { students, totalPages } = response.data;
      setStudents(students);
      setTotalPages(totalPages); // Обновляем общее количество страниц
    } catch (error) {
      console.error('Error fetching students:', error.message);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [currentPage, pageSize]); // Перезапрос при изменении страницы или размера страницы

  // Обработчик изменения данных формы
  const handleInputChange = (event) => {
    const value = event.target.value;
    setFormData({
      ...formData,
      [event.target.name]: value,
    });
  };

  // Обработчик отправки формы
  const handleFromSubmit = async (event) => {
    event.preventDefault();

    try {
      const infoStudent = {
        last_name: formData.last_name,
        first_name: formData.first_name,
        patronymic: formData.patronymic,
        study_year: parseInt(formData.study_year, 10),
        group_name: formData.group_name,
        faculty_name: formData.faculty_name
      };

      const isDeleteAction = event.nativeEvent.submitter.classList.contains('btn-delete'); // Проверяем, нажата ли кнопка "Удалить"

      if (isDeleteAction) {
        // Удаление студента
        try {
          await api.delete('/delete/', { data: infoStudent });
          console.log('Student deleted successfully');
        } catch (error) {
          console.error('Error deleting student:', error.message);
        }
      } else {
        // Добавление нового студента
        try {
          await api.post('/create/', infoStudent);
          console.log('Student added successfully');
        } catch (error) {
          console.error('Error adding student:', error.message);
        }
      }

      fetchStudents(); // Обновляем таблицу после добавления
      setFormData({ last_name: '', first_name: '', patronymic: '', study_year: '', group_name: '', faculty_name: '' });
    } catch (error) {
      console.error('Error adding student:', error.message);
    }
  };

  // Функции для переключения страниц
  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const goToPreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  // Обработчик изменения размера страницы
  const handlePageSizeChange = (event) => {
    setPageSize(Number(event.target.value));
    setCurrentPage(1); // Сбрасываем на первую страницу при изменении размера
  };

  // Обработчик перехода на конкретную страницу
  const goToPage = (page) => {
    setCurrentPage(page);
  };

  return (
    <div>
      <nav>
        <div>
          <a href="#">
            Students Admin's Panel
          </a>
        </div>
      </nav>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <form onSubmit={handleFromSubmit}>
            <div>
              <h1>Добавить или удалить запись</h1>
              <input type="text" id="last_name" name="last_name" placeholder="Фамилия" onChange={handleInputChange} value={formData.last_name}></input>
              <input type="text" id="first_name" name="first_name" placeholder="Имя" onChange={handleInputChange} value={formData.first_name}></input>
              <input type="text" id="patronymic" name="patronymic" placeholder="Отчество" onChange={handleInputChange} value={formData.patronymic}></input>
              <input type="text" id="study_year" name="study_year" placeholder="Год обучения" onChange={handleInputChange} value={formData.study_year}></input>
              <input type="text" id="group_name" name="group_name" placeholder="Группа" onChange={handleInputChange} value={formData.group_name}></input>
              <input type="text" id="faculty_name" name="faculty_name" placeholder="Факультет" onChange={handleInputChange} value={formData.faculty_name}></input>
            </div>

            <div className="div-btns">
              <button className="btn-submit" type="submit">
                Submit
              </button>
            
              <button className="btn-delete" type="delete">
                Delete
              </button>
            </div>
          </form>
        </div>

        <table>
          <thead>
            <tr>
              <th>Фамилия</th>
              <th>Имя</th>
              <th>Отчество</th>
              <th>Год обучения</th>
              <th>Группа</th>
              <th>Факультет</th>
            </tr>
          </thead>
          <tbody>
            {students.map((student) => (
              <tr key={`${student.last_name}-${student.first_name}-${student.patronymic}`}>
                <td>{student.last_name}</td>
                <td>{student.first_name}</td>
                <td>{student.patronymic}</td>
                <td>{student.study_year}</td>
                <td>{student.group_name}</td>
                <td>{student.faculty_name}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Пагинация */}
        <div className="pagination-controls">
          <div className="page-size-control">
            <label htmlFor="pageSize">Select page size:</label>
            <select id="pageSize" value={pageSize} onChange={handlePageSizeChange}>
              <option value={10}>10 items per page</option>
              <option value={25}>25 items per page</option>
              <option value={50}>50 items per page</option>
            </select>
          </div>

          <div className="page-input-control">
            <button className="pagination-btn" onClick={goToPreviousPage} disabled={currentPage === 1}>
              Previous
            </button>
            <label htmlFor="pageInput">Go to page:</label>
            <input
              type="number"
              id="pageInput"
              value={currentPage}
              onChange={(e) => {
                const page = Math.max(1, Math.min(totalPages, Number(e.target.value)));
                setCurrentPage(page);
              }}
              min={1}
              max={totalPages}
            />
            <button className="pagination-btn" onClick={goToNextPage} disabled={currentPage === totalPages}>
              Next
            </button>
          </div>

          <div className="pagination-status">
            <span>Page {currentPage} of {totalPages}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
