# frontend/Dockerfile

# --- ЭТАП 1: Сборка ---
# Используем официальный образ Node.js для сборки нашего приложения
FROM node:18-alpine AS build

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем package.json и package-lock.json для установки зависимостей
# Используем '*', чтобы скопировать оба файла, если они существуют
COPY package*.json ./

# Гарантируем чистую установку, удаляя старые зависимости
# Это решает проблемы с конфликтом версий esbuild и другими кэшированными ошибками
RUN rm -rf node_modules package-lock.json
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
# Убедитесь, что у вас есть файл nginx.conf рядом с этим Dockerfile
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80, который использует Nginx
EXPOSE 80

# Команда для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]