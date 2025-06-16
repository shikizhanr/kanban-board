import React, { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Spinner from '../components/Spinner';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('accessToken'));
    const [loading, setLoading] = useState(true);

    const navigate = useNavigate();

    useEffect(() => {
        const initializeAuth = async () => {
            if (token) {
                // Если у нас есть токен, мы можем добавить запрос к бэкенду
                // для получения данных о текущем пользователе, например, GET /users/me
                // Это сделает приложение более надежным.
                // Пока что мы просто доверяем наличию токена.
            }
            setLoading(false);
        };
        initializeAuth();
    }, [token]);

    const login = async (email, password) => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        const response = await api.post('/auth/token', params);
        const { access_token } = response.data;

        localStorage.setItem('accessToken', access_token);
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        setToken(access_token);
        navigate('/');
    };

    const register = async (userData) => {
        await api.post('/users/', userData);
        navigate('/login');
    };

    const logout = () => {
        localStorage.removeItem('accessToken');
        delete api.defaults.headers.common['Authorization'];
        setUser(null);
        setToken(null);
        navigate('/login');
    };

    const value = { token, user, login, register, logout, isLoggedIn: !!token };

    if (loading) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
