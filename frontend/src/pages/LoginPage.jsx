import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import Spinner from '../components/Spinner';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(email, password);
        } catch (err) {
            setError('Неверный логин или пароль.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
            <div className="w-full max-w-md">
                <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-lg">
                    <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Вход в систему</h2>
                    {error && <p className="bg-red-100 text-red-700 p-3 rounded-md mb-4 text-sm">{error}</p>}
                    <div className="mb-4">
                        <label className="block text-gray-700 mb-2" htmlFor="email">Email</label>
                        <input type="email" id="email" value={email} onChange={e => setEmail(e.target.value)} required className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                    <div className="mb-6">
                        <label className="block text-gray-700 mb-2" htmlFor="password">Пароль</label>
                        <input type="password" id="password" value={password} onChange={e => setPassword(e.target.value)} required className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                    <button type="submit" disabled={loading} className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition duration-300 disabled:bg-indigo-300 flex justify-center items-center h-10">
                        {loading ? <Spinner /> : 'Войти'}
                    </button>
                    <p className="text-center text-sm text-gray-500 mt-6">
                        Нет аккаунта? <Link to="/register" className="text-indigo-600 hover:underline">Зарегистрироваться</Link>
                    </p>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;