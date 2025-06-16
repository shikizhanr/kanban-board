import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import api from '../api';
import Spinner from '../components/Spinner';

const ProfilePage = () => {
    const { user, logout } = useAuth();
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Пожалуйста, выберите файл для загрузки.');
            return;
        }
        setLoading(true);
        setError('');
        
        const formData = new FormData();
        formData.append('file', file);

        try {
            await api.post('/users/me/avatar', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            // После успешной загрузки можно было бы обновить стейт пользователя,
            // но для простоты мы просто перезагрузим страницу.
            window.location.reload(); 
        } catch (err) {
            setError('Не удалось загрузить аватар.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (!user) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }

    return (
        <div className="flex flex-col h-screen bg-neutral-900 text-white font-sans">
            <header className="bg-neutral-800 border-b border-neutral-700 p-4 flex justify-between items-center">
                 <h1 className="text-2xl font-bold text-indigo-400">Личный кабинет</h1>
                 <div className="flex items-center space-x-4">
                     <Link to="/" className="text-neutral-400 hover:text-white transition-colors">Назад к доске</Link>
                     <button onClick={logout} className="bg-red-600/50 text-white px-4 py-2 rounded-lg hover:bg-red-500/50 text-sm font-semibold">Выйти</button>
                 </div>
            </header>
            <main className="flex-grow p-8 flex items-center justify-center">
                <div className="bg-neutral-800 p-8 rounded-lg shadow-lg w-full max-w-md">
                    <div className="flex flex-col items-center space-y-4">
                        <div className="relative">
                            <img 
                                src={preview || (user.avatar_url ? `http://localhost:8000/${user.avatar_url}` : 'https://placehold.co/128x128/1f2937/a7a7a7?text=??')} 
                                alt="avatar" 
                                className="w-32 h-32 rounded-full object-cover border-4 border-indigo-500" 
                            />
                        </div>
                         <h2 className="text-2xl font-bold">{user.first_name} {user.last_name}</h2>
                         <p className="text-neutral-400">{user.email}</p>
                    </div>
                     <form onSubmit={handleSubmit} className="mt-8">
                        <label className="block text-sm font-medium text-neutral-400 mb-2">Сменить аватар</label>
                        <input 
                            type="file" 
                            onChange={handleFileChange}
                            accept="image/png, image/jpeg"
                            className="block w-full text-sm text-neutral-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600/20 file:text-indigo-300 hover:file:bg-indigo-600/30"
                        />
                        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
                        <button type="submit" disabled={loading || !file} className="w-full mt-6 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-500 transition duration-300 disabled:bg-neutral-700 disabled:cursor-not-allowed flex justify-center items-center h-10">
                            {loading ? <Spinner /> : 'Сохранить новый аватар'}
                        </button>
                    </form>
                </div>
            </main>
        </div>
    );
};

export default ProfilePage;