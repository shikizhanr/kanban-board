import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import api from '../api';
import Spinner from '../components/Spinner';
import ThemeToggleButton from '../components/ThemeToggleButton'; // Import ThemeToggleButton

const ProfilePage = () => {
    const { user, logout, updateUser } = useAuth();
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
            const response = await api.post('/users/me/avatar', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            console.log('Avatar upload response data:', response.data); // Log the response
            const newUserData = response.data;
            newUserData.avatar_last_updated = new Date().getTime();
            updateUser(newUserData); // Update user in AuthContext
            setFile(null); // Reset file input
            setPreview(null); // Reset preview
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

    // Determine avatarSrc
    let avatarSrc = 'https://placehold.co/128x128/e2e8f0/4a5568?text=??'; // Default placeholder
    if (preview) {
        avatarSrc = preview;
    } else if (user && typeof user.avatar_url === 'string' && user.avatar_url.trim() !== '') {
        // Ensure user.avatar_url is a non-empty string before using it
        const path = user.avatar_url; // Assign to a temporary variable
        // Assuming path is like "uploads/user_id_filename.png"
        avatarSrc = `http://localhost:8000/api/${path}?v=${user.avatar_last_updated || '0'}`; 
    }

    return (
        <div className="flex flex-col h-screen bg-white dark:bg-neutral-900 text-neutral-800 dark:text-white font-sans">
            <header className="bg-neutral-100 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 p-4 flex justify-between items-center">
                 <h1 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">Личный кабинет</h1>
                 <div className="flex items-center space-x-4">
                     <ThemeToggleButton /> {/* Add ThemeToggleButton here */}
                     <Link to="/my-tasks" className="text-sm font-medium text-neutral-600 dark:text-neutral-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                         Мои задачи
                     </Link>
                     <Link to="/" className="text-sm font-medium text-neutral-600 dark:text-neutral-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"> {/* Adjusted class for consistency */}
                        Назад к доске
                     </Link>
                     <button onClick={logout} className="bg-red-500 hover:bg-red-600 dark:bg-red-600/50 dark:hover:bg-red-500/50 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">Выйти</button>
                 </div>
            </header>
            <main className="flex-grow p-8 flex items-center justify-center">
                <div className="bg-neutral-100 dark:bg-neutral-800 p-8 rounded-lg shadow-lg w-full max-w-md">
                    <div className="flex flex-col items-center space-y-4">
                        <div className="relative">
                            <img 
                                src={avatarSrc}
                                alt="avatar" 
                                className="w-32 h-32 rounded-full object-cover border-4 border-indigo-500 dark:border-indigo-500"
                                onError={(e) => {
                                    console.error('Avatar image failed to load:', e.target.src);
                                    // Optionally, set a specific error state here to show a message in the UI
                                    // setError('Avatar image could not be loaded. Please try uploading again or contact support.');
                                }}
                            />
                        </div>
                         <h2 className="text-2xl font-bold text-neutral-800 dark:text-white">{user.first_name} {user.last_name}</h2>
                         <p className="text-neutral-500 dark:text-neutral-400">{user.email}</p>
                    </div>
                     <form onSubmit={handleSubmit} className="mt-8">
                        <label className="block text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-2">Сменить аватар</label>
                        <input 
                            type="file" 
                            onChange={handleFileChange}
                            accept="image/png, image/jpeg"
                            className="block w-full text-sm text-neutral-500 dark:text-neutral-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-100 dark:file:bg-indigo-600/20 file:text-indigo-700 dark:file:text-indigo-300 hover:file:bg-indigo-200 dark:hover:file:bg-indigo-600/30 transition-colors"
                        />
                        {error && <p className="text-red-500 dark:text-red-400 text-sm mt-2">{error}</p>}
                        <button type="submit" disabled={loading || !file} className="w-full mt-6 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-500 transition duration-300 disabled:bg-indigo-400 dark:disabled:bg-neutral-700 disabled:cursor-not-allowed flex justify-center items-center h-10">
                            {loading ? <Spinner /> : 'Сохранить новый аватар'}
                        </button>
                    </form>
                </div>
            </main>
        </div>
    );
};

export default ProfilePage;