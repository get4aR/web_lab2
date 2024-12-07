import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Основной компонент приложения

// Создание корневого рендера React
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
