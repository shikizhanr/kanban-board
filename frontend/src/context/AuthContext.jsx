import React, { createContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Spinner from '../components/Spinner';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {   
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const navigate = useNavigate();

    // Функция для выхода из системы
    const logout = useCallback(() => {
        localStorage.removeItem('accessToken');
        delete api.defaults.headers.common['Authorization'];
        setUser(null);
        navigate('/login', { replace: true });
    }, [navigate]);

    // Функция для проверки токена и загрузки данных пользователя
    const fetchUser = useCallback(async () => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            try {
                api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                const response = await api.get('/users/me');
                setUser(response.data);
            } catch (error) {
                console.error("Не удалось получить данные пользователя, токен недействителен.", error);
                logout();
            }
        }
        setLoading(false);
    }, [logout]);

    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    const login = async (email, password) => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        const response = await api.post('/auth/token', params);
        const { access_token } = response.data;
        localStorage.setItem('accessToken', access_token);
        
        await fetchUser(); 
        navigate('/', { replace: true });
    };

    const register = async (userData) => {
        await api.post('/users/', userData);
        navigate('/login');
    };

    const updateUser = (newUserData) => {
        setUser(newUserData);
    };

    const value = { user, login, register, logout, updateUser, isLoggedIn: !!user };

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