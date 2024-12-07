FROM node:20 AS build

# Рабочая директория
WORKDIR /app

# Копируем package.json и package-lock.json для установки зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все файлы приложения в рабочую директорию проекта
COPY . .

# Собираем приложение
RUN npm run build

# Этап настройка и создания Nginx
FROM nginx:latest

# Копируем конфигурацию
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем сборку React в папку Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Открываем порт 80
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]