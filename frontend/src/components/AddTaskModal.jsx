
import React, { useState, useEffect } from 'react';
import api from '../api';
import Spinner from './Spinner';

const AddTaskModal = ({ isOpen, onClose, onTaskAdded }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [type, setType] = useState('development');
    const [assigneeId, setAssigneeId] = useState('');
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (isOpen && users.length === 0) {
            const fetchUsers = async () => {
                try {
                    const response = await api.get('/users/');
                    setUsers(response.data);
                } catch (err) {
                    console.error("Failed to fetch users", err);
                    setError("Не удалось загрузить список пользователей.");
                }
            };
            fetchUsers();
        }
    }, [isOpen, users.length]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const taskData = {
                title,
                description,
                type,
                assignee_id: assigneeId ? parseInt(assigneeId, 10) : null,
            };
            const response = await api.post('/tasks/', taskData);
            onTaskAdded(response.data); 
            handleClose();
        } catch (err) {
            console.error("Failed to create task", err);
            setError("Не удалось создать задачу. Проверьте введенные данные.");
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setTitle('');
        setDescription('');
        setType('development');
        setAssigneeId('');
        setError('');
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-lg">
                <h2 className="text-2xl font-bold mb-6">Создать новую задачу</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-gray-700 mb-2">Название</label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="w-full px-4 py-2 border rounded-lg"
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block text-gray-700 mb-2">Описание</label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="w-full px-4 py-2 border rounded-lg"
                            rows="3"
                        ></textarea>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mb-6">
                        <div>
                            <label className="block text-gray-700 mb-2">Тип задачи</label>
                            <select value={type} onChange={(e) => setType(e.target.value)} className="w-full px-4 py-2 border rounded-lg">
                                <option value="development">Разработка</option>
                                <option value="analytics">Аналитика</option>
                                <option value="documentation">Документация</option>
                                <option value="testing">Тестирование</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-gray-700 mb-2">Исполнитель</label>
                            <select value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)} className="w-full px-4 py-2 border rounded-lg">
                                <option value="">Не назначен</option>
                                {users.map(user => (
                                    <option key={user.id} value={user.id}>
                                        {user.first_name} {user.last_name}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

                    <div className="flex justify-end space-x-4">
                        <button type="button" onClick={handleClose} className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300">
                            Отмена
                        </button>
                        <button type="submit" disabled={loading} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-indigo-300 flex items-center">
                            {loading && <Spinner />}
                            <span className={loading ? 'ml-2' : ''}>Создать</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddTaskModal;