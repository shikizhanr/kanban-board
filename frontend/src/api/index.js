import axios from 'axios';

// Создаем экземпляр axios с базовым URL вашего бэкенда
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
});

// Axios Interceptor: Эта функция будет автоматически добавлять
// токен аутентификации в заголовок каждого запроса, если он есть в localStorage.
api.interceptors.request.use(config => {
    const token = localStorage.getItem('accessToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

// Реализовал удаление задачи
export const deleteTask = (taskId) => {
    return api.delete(`/tasks/${taskId}`);
};

export default api;