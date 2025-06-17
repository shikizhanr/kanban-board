import React, { useState, useEffect } from 'react';
import api from '../api';
import Spinner from './Spinner';

const EditTaskModal = ({ isOpen, onClose, onTaskUpdated, task, onDelete }) => { // Added onDelete
    // Состояния для полей формы
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [type, setType] = useState('development');
    const [priority, setPriority] = useState('medium'); // Added priority state
    const [assigneeIds, setAssigneeIds] = useState([]); // Храним ID исполнителей в виде массива

    // Вспомогательные состояния
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        // Загружаем пользователей один раз, когда модальное окно открывается
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

    useEffect(() => {
        if (isOpen && task) {
            setTitle(task.title);
            setDescription(task.description || '');
            setType(task.type);
            setPriority(task.priority || 'medium'); // Set priority from task
            setAssigneeIds(task.assignees ? task.assignees.map(user => user.id) : []);
        } else if (!isOpen) {
            // resetForm(); // Already handled by handleClose
        }
    }, [task, isOpen]);

    // Обработчик для выбора/снятия выбора исполнителя
    const handleAssigneeChange = (userId) => {
        setAssigneeIds(prev =>
            prev.includes(userId)
                ? prev.filter(id => id !== userId) // убираем, если уже есть
                : [...prev, userId] // добавляем, если нет
        );
    };

    // Сброс формы в исходное состояние
    const resetForm = () => {
        setTitle('');
        setDescription('');
        setType('development');
        setPriority('medium'); // Reset priority
        setAssigneeIds([]);
        setError('');
        setLoading(false);
    };

    const handleClose = () => {
        resetForm();
        onClose();
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (!task || !task.id) {
            setError("Task data is missing.");
            setLoading(false);
            return;
        }

        try {
            const taskData = {
                title,
                description,
                type,
                priority, // Include priority
                assignee_ids: assigneeIds,
            };
            const response = await api.put(`/tasks/${task.id}/`, taskData);
            onTaskUpdated(response.data);
            handleClose();
        } catch (err) {
            console.error("Failed to update task", err);
            setError(err.response?.data?.detail || "Не удалось обновить задачу. Проверьте введенные данные.");
        } finally {
            setLoading(false);
        }
    };

    // New handleDelete function
    const handleDelete = () => {
        if (window.confirm('Вы уверены, что хотите удалить эту задачу?')) {
            if (onDelete && task && task.id) {
                onDelete(task.id); // Call the callback passed from parent
                // Modal closure is handled by the parent after successful deletion.
            }
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-60 flex justify-center items-center z-50 p-4">
            <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-xl p-6 md:p-8 w-full max-w-lg border border-neutral-200 dark:border-neutral-700">
                <h2 className="text-2xl font-bold mb-6 text-neutral-800 dark:text-neutral-100">Редактировать задачу</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-neutral-600 dark:text-neutral-400 mb-2 text-sm">Название</label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="w-full px-4 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-neutral-800 dark:text-neutral-100"
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block text-neutral-600 dark:text-neutral-400 mb-2 text-sm">Описание</label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="w-full px-4 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-neutral-800 dark:text-neutral-100"
                            rows="3"
                        ></textarea>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"> {/* Adjusted grid to fit priority */}
                        <div>
                            <label className="block text-neutral-600 dark:text-neutral-400 mb-2 text-sm">Тип задачи</label>
                            <select value={type} onChange={(e) => setType(e.target.value)} className="w-full px-4 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-neutral-800 dark:text-neutral-100">
                                <option value="development">Разработка</option>
                                <option value="analytics">Аналитика</option>
                                <option value="documentation">Документация</option>
                                <option value="testing">Тестирование</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-neutral-600 dark:text-neutral-400 mb-2 text-sm">Приоритет</label>
                            <select value={priority} onChange={(e) => setPriority(e.target.value)} className="w-full px-4 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-neutral-800 dark:text-neutral-100">
                                <option value="low">Низкий</option>
                                <option value="medium">Средний</option>
                                <option value="high">Высокий</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-neutral-600 dark:text-neutral-400 mb-2 text-sm">Исполнители</label>
                            <div className="max-h-32 overflow-y-auto bg-neutral-50 dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg p-2 space-y-1">
                                {users.length > 0 ? users.map(user => (
                                    <div key={user.id} className="flex items-center space-x-3 p-2 hover:bg-neutral-200 dark:hover:bg-neutral-600/50 rounded-md">
                                        <input
                                            type="checkbox"
                                            id={`edit-user-${user.id}`}
                                            checked={assigneeIds.includes(user.id)}
                                            onChange={() => handleAssigneeChange(user.id)}
                                            className="h-4 w-4 rounded bg-neutral-200 dark:bg-neutral-600 border-neutral-400 dark:border-neutral-500 text-indigo-600 dark:text-indigo-500 focus:ring-indigo-500"
                                        />
                                        <label htmlFor={`edit-user-${user.id}`} className="text-sm text-neutral-700 dark:text-neutral-300">
                                            {user.first_name} {user.last_name}
                                        </label>
                                    </div>
                                )) : <p className="text-neutral-500 dark:text-neutral-500 text-sm p-2">Пользователи не найдены.</p>}
                            </div>
                        </div>
                    </div>

                    {error && <p className="text-red-500 dark:text-red-400 text-sm mb-4">{error}</p>}

                    {/* Modified Footer Buttons */}
                    <div className="flex justify-between items-center w-full pt-4 border-t border-neutral-200 dark:border-neutral-700">
                        <div> {/* Container for Delete button on the left */}
                            {onDelete && task && task.id && (
                                <button
                                    type="button"
                                    onClick={handleDelete}
                                    disabled={loading} // Disable if save is in progress
                                    className="px-4 py-2 bg-red-500 hover:bg-red-600 dark:bg-red-700 dark:hover:bg-red-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Удалить
                                </button>
                            )}
                        </div>
                        <div className="flex space-x-4"> {/* Container for Cancel and Save buttons on the right */}
                            <button type="button" onClick={handleClose} className="px-4 py-2 bg-neutral-200 dark:bg-neutral-600 text-neutral-800 dark:text-neutral-100 rounded-lg hover:bg-neutral-300 dark:hover:bg-neutral-500 transition-colors">
                                Отмена
                            </button>
                            <button type="submit" disabled={loading} className="px-5 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-500 transition-colors disabled:bg-indigo-400 dark:disabled:bg-neutral-700 disabled:cursor-not-allowed flex items-center justify-center min-w-[100px]">
                                {loading ? <Spinner size="sm" /> : 'Сохранить'}
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditTaskModal;