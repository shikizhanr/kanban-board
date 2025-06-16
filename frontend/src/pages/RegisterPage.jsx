import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import Spinner from '../components/Spinner';

const RegisterPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await register({ email, password, first_name: firstName, last_name: lastName });
        } catch (err) {
            console.error("Registration failed", err);
            if (err.response && err.response.status === 422) {
                // Если это ошибка валидации от FastAPI, форматируем сообщение
                const errorDetail = err.response.data.detail[0];
                const field = errorDetail.loc[1]; // e.g., 'password'
                const message = errorDetail.msg; // e.g., 'String should have at least 8 characters'
                setError(`Ошибка в поле '${field}': ${message}`);
            } else if (err.response && err.response.status === 400) {
                 setError("Пользователь с таким email уже существует.");
            } else {
                setError('Произошла неизвестная ошибка при регистрации.');
            }
            // --- КОНЕЦ УЛУЧШЕНИЙ ---
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
            <div className="w-full max-w-md">
                <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-lg">
                    <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Регистрация</h2>
                    {error && <p className="bg-red-100 text-red-700 p-3 rounded-md mb-4 text-sm">{error}</p>}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <label className="block text-gray-700 mb-2" htmlFor="firstName">Имя</label>
                            <input type="text" id="firstName" value={firstName} onChange={e => setFirstName(e.target.value)} required className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <div>
                            <label className="block text-gray-700 mb-2" htmlFor="lastName">Фамилия</label>
                            <input type="text" id="lastName" value={lastName} onChange={e => setLastName(e.target.value)} required className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                    </div>
                    <div className="mb-4">
                        <label className="block text-gray-700 mb-2" htmlFor="email">Email</label>
                        <input type="email" id="email" value={email} onChange={e => setEmail(e.target.value)} required className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                    <div className="mb-6">
                        <label className="block text-gray-700 mb-2" htmlFor="password">Пароль (мин. 8 символов)</label>
                        <input type="password" id="password" value={password} onChange={e => setPassword(e.target.value)} required className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                    <button type="submit" disabled={loading} className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition duration-300 disabled:bg-indigo-300 flex justify-center items-center h-10">
                        {loading ? <Spinner /> : 'Зарегистрироваться'}
                    </button>
                    <p className="text-center text-sm text-gray-500 mt-6">
                        Уже есть аккаунт? <Link to="/login" className="text-indigo-600 hover:underline">Войти</Link>
                    </p>
                </form>
            </div>
        </div>
    );
};

export default RegisterPage;