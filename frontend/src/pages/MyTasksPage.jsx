import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api, { deleteTask } from '../api'; // Ensure deleteTask is imported
import useAuth from '../hooks/useAuth';
import TaskCard from '../components/TaskCard';
import Spinner from '../components/Spinner';
import ThemeToggleButton from '../components/ThemeToggleButton';
import EditTaskModal from '../components/EditTaskModal'; // Import EditTaskModal
import ConfirmationModal from '../components/ConfirmationModal'; // Import ConfirmationModal

const MyTasksPage = () => {
    const [myTasks, setMyTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { user, logout } = useAuth();
    const [editingTask, setEditingTask] = useState(null); // State for task being edited
    const [isEditModalOpen, setIsEditModalOpen] = useState(false); // State for modal visibility

    // New states for delete confirmation
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [taskToDeleteId, setTaskToDeleteId] = useState(null);
    const [taskToDeleteTitle, setTaskToDeleteTitle] = useState('');


    const fetchMyTasks = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const response = await api.get('/users/me/tasks');
            setMyTasks(response.data);
        } catch (err) {
            setError('Не удалось загрузить ваши задачи.');
            console.error("Failed to fetch user's tasks", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchMyTasks();
    }, [fetchMyTasks]);

    const handleTaskUpdated = (updatedTask) => {
        setMyTasks(prevTasks => prevTasks.map(task =>
            task.id === updatedTask.id ? updatedTask : task
        ));
        // Optionally, re-fetch or ensure sorting is maintained if priority changed
        // fetchMyTasks(); // Or smarter update
    };

    const openEditModal = (task) => {
        setEditingTask(task);
        setIsEditModalOpen(true);
        setError(''); // Clear page errors when opening modal
    };
    const closeEditModal = () => {
        setEditingTask(null);
        setIsEditModalOpen(false);
        setError(''); // Clear page errors when closing modal by cancel/X
    };

    // Modified handleDeleteTask to open confirmation modal
    const handleDeleteTask = (taskId, taskTitle) => {
        setTaskToDeleteId(taskId);
        setTaskToDeleteTitle(taskTitle);
        setShowDeleteConfirm(true);
        setError(''); // Clear previous errors
    };

    // New function to execute deletion after confirmation
    const executeDeleteTask = async () => {
        if (!taskToDeleteId) return;
        setError('');
        try {
            await deleteTask(taskToDeleteId);
            setMyTasks(prevTasks => prevTasks.filter(task => task.id !== taskToDeleteId));
        } catch (err) {
            setError('Не удалось удалить задачу. Попробуйте еще раз.');
            console.error('Failed to delete task on MyTasksPage', err);
        } finally {
            setShowDeleteConfirm(false);
            setTaskToDeleteId(null);
            setTaskToDeleteTitle('');
        }
    };

    // New function for handling delete from EditTaskModal (which has its own internal confirmation)
    const handleApiDeleteFromEditModal = async (taskId) => {
        setError(''); // Clear previous page-level errors
        try {
            await deleteTask(taskId);
            setMyTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
            // Close EditTaskModal by resetting its controlling states
            setEditingTask(null);
            setIsEditModalOpen(false);
            // Optionally, display a success notification
        } catch (err) {
            console.error('Failed to delete task from EditTaskModal on MyTasksPage:', err);
            // Set page-level error. EditTaskModal might also show its own error if the API call was made from it.
            // However, EditTaskModal's onDelete is a callback *after* its internal confirmation.
            // So, this error is from the API call made here in MyTasksPage.
            setError(err.response?.data?.detail || 'Не удалось удалить задачу. Попробуйте еще раз.');
            // Modal should ideally remain open or its error state be set.
            // Since we are setting page-level error, and not closing modal on error here, it will stay open.
        }
    };


    if (loading) {
        return (
            <div className="flex flex-col h-screen bg-white dark:bg-neutral-900 text-neutral-800 dark:text-white">
                <div className="flex justify-center items-center h-full">
                    <Spinner />
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col min-h-screen bg-white dark:bg-neutral-900 text-neutral-800 dark:text-white font-sans">
            <header className="bg-neutral-100 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 p-4 flex justify-between items-center flex-shrink-0">
                <h1 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">Мои задачи</h1>
                <div className="flex items-center space-x-4">
                    <ThemeToggleButton />
                    <Link to="/" className="text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white transition-colors">
                        Доска
                    </Link>
                    <Link to="/profile" className="text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white transition-colors">
                        Профиль
                    </Link>
                    <button onClick={logout} className="bg-red-500 hover:bg-red-600 dark:bg-red-600/50 dark:hover:bg-red-500/50 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                        Выйти
                    </button>
                </div>
            </header>
            <main className="flex-grow p-4 md:p-6 lg:p-8">
                {error && (
                    <div className="text-center text-red-500 dark:text-red-400 my-4 p-3 bg-red-100 dark:bg-red-900/30 rounded-md">
                        {error}
                    </div>
                )}
                {myTasks.length === 0 && !error && (
                    <div className="text-center text-neutral-500 dark:text-neutral-400 mt-10">
                        У вас пока нет назначенных или созданных задач.
                    </div>
                )}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    {myTasks.map(task => (
                        // Note: TaskCard expects 'provided' prop for react-beautiful-dnd, which is not used here.
                        // We'll pass minimal dnd props or modify TaskCard if it causes issues.
                        // For now, passing undefined or minimal mock.
                        <TaskCard
                            key={task.id}
                            task={task}
                            onClick={() => openEditModal(task)}
                            provided={{ innerRef: React.createRef(), draggableProps: {}, dragHandleProps: {} }}
                            onDelete={() => handleDeleteTask(task.id, task.title)} // Updated to pass title
                        />
                    ))}
                </div>
            </main>
            <EditTaskModal
                isOpen={isEditModalOpen}
                onClose={closeEditModal}
                onTaskUpdated={handleTaskUpdated}
                task={editingTask}
                onDelete={handleApiDeleteFromEditModal} // Pass the new handler here
            />
            {showDeleteConfirm && (
                <ConfirmationModal
                    isOpen={showDeleteConfirm}
                    onClose={() => {
                        setShowDeleteConfirm(false);
                        setTaskToDeleteId(null);
                        setTaskToDeleteTitle('');
                    }}
                    onConfirm={executeDeleteTask}
                    title="Подтверждение удаления"
                    message={`Вы уверены, что хотите удалить задачу "${taskToDeleteTitle}"? Это действие необратимо.`}
                    confirmButtonText="Удалить"
                    cancelButtonText="Отмена"
                    confirmButtonColor="red"
                />
            )}
        </div>
    );
};

export default MyTasksPage;