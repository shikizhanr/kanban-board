# --- ЭТАП 1: Сборка ---
# Используем официальный образ Node.js для сборки нашего приложения
FROM node:18-alpine AS build

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем package.json и package-lock.json для установки зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальные файлы нашего приложения
COPY . .

# Собираем статические файлы для продакшена
RUN npm run build

# --- ЭТАП 2: Запуск ---
# Используем легкий образ Nginx для раздачи статических файлов
FROM nginx:stable-alpine

# Копируем собранные статические файлы из этапа "build" в папку Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем наш файл конфигурации для Nginx
# (мы создадим его в следующем шаге)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80, который использует Nginx
EXPOSE 80

# Команда для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]