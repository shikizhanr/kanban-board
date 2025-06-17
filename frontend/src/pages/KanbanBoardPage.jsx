import React, { useState, useEffect, useCallback } from 'react';
import { DragDropContext } from '@hello-pangea/dnd';
import { Link } from 'react-router-dom';
import api from '../api';
import useAuth from '../hooks/useAuth';
import KanbanColumn from '../components/KanbanColumn';
import Spinner from '../components/Spinner';
import AddTaskModal from '../components/AddTaskModal';
import EditTaskModal from '../components/EditTaskModal';
import ThemeToggleButton from '../components/ThemeToggleButton'; // Import ThemeToggleButton

const KanbanBoardPage = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { user, logout } = useAuth();
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [editingTask, setEditingTask] = useState(null);

    const columns = {
        todo: { id: 'todo', title: 'Запланировано' },
        in_progress: { id: 'in_progress', title: 'В работе' },
        done: { id: 'done', title: 'Готово' },
    };

    const fetchTasks = useCallback(async () => {
        setLoading(true);
        try {
            const response = await api.get('/tasks/');
            setTasks(response.data);
        } catch (err) {
            setError('Не удалось загрузить задачи.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTasks();
    }, [fetchTasks]);

    const handleTaskAdded = (newTask) => {
        setTasks(prevTasks => [...prevTasks, newTask]);
    };

    const handleTaskUpdated = (updatedTask) => {
        setTasks(prevTasks => prevTasks.map(task =>
            task.id === updatedTask.id ? updatedTask : task
        ));
    };

    const handleTaskDeleted = (deletedTaskId) => {
        setTasks(prevTasks => prevTasks.filter(task => task.id !== deletedTaskId));
    };

    const onDragEnd = async (result) => {
        const { source, destination, draggableId } = result;
        if (!destination || (source.droppableId === destination.droppableId && source.index === destination.index)) {
            return;
        }

        const taskId = parseInt(draggableId);
        const newStatus = destination.droppableId;
        const currentTasks = tasks;

        const updatedTasks = tasks.map(task =>
            task.id === taskId ? { ...task, status: newStatus } : task
        );
        setTasks(updatedTasks);

        try {
            await api.put(`/tasks/${taskId}`, { status: newStatus });
        } catch (err) {
            setError('Не удалось обновить статус задачи.');
            console.error(err);
            setTasks(currentTasks);
        }
    };

    
    const handleTaskClick = useCallback((task) => {
        setEditingTask(task);
    }, []);

    if (loading) return <div className="flex justify-center items-center h-screen bg-white dark:bg-neutral-900"><Spinner /></div>;
    if (error) return <div className="text-center text-red-500 dark:text-red-400 mt-10">{error}</div>;

    return (
        <div className="flex flex-col h-screen bg-white dark:bg-neutral-900 text-neutral-800 dark:text-white font-sans">
            <header className="bg-neutral-100 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 p-4 flex justify-between items-center flex-shrink-0">
                <h1 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">Kanban.PRO</h1>
                <div className="flex items-center space-x-6">
                    <button
                        onClick={() => setIsAddModalOpen(true)}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-500 transition-colors text-sm font-semibold"
                    >
                        + Создать задачу
                    </button>
                    <ThemeToggleButton /> {/* Add ThemeToggleButton here */}
                    <Link to="/my-tasks" className="text-sm font-medium text-neutral-600 dark:text-neutral-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                        Мои задачи
                    </Link>
                    <div className="flex items-center space-x-4">
                        <Link to="/profile" className="w-9 h-9 bg-neutral-200 dark:bg-neutral-700 rounded-full flex items-center justify-center text-sm font-bold hover:bg-neutral-300 dark:hover:bg-neutral-600 transition-colors" title="Профиль">
                           {user?.avatar_url ? (
                               <img src={`http://localhost:8000/api/${user.avatar_url}?v=${user.avatar_last_updated || '0'}`} alt="avatar" className="w-full h-full rounded-full object-cover" />
                           ) : (
                               <svg className="text-neutral-600 dark:text-neutral-400" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                           )}
                        </Link>
                        <button onClick={logout} className="text-neutral-500 dark:text-neutral-400 hover:text-neutral-800 dark:hover:text-white transition-colors" title="Выйти">
                            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                        </button>
                    </div>
                </div>
            </header>
            <main className="flex-grow p-4 md:p-6 lg:p-8 overflow-x-auto bg-neutral-50 dark:bg-neutral-800/30">
                <DragDropContext onDragEnd={onDragEnd}>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full">
                        {Object.values(columns).map(column => {
                            const columnTasks = tasks.filter(task => task.status === column.id);
                            return (
                                <KanbanColumn
                                    key={column.id}
                                    column={column}
                                    tasks={columnTasks}
                                    onTaskClick={(task) => setEditingTask(task)}
                                />
                            );
                        })}
                    </div>
                </DragDropContext>
            </main>
            <AddTaskModal
                isOpen={isAddModalOpen}
                onClose={() => setIsAddModalOpen(false)}
                onTaskAdded={handleTaskAdded}
            />
            <EditTaskModal
                isOpen={!!editingTask}
                onClose={() => setEditingTask(null)}
                onTaskUpdated={handleTaskUpdated}
                onTaskDeleted={handleTaskDeleted} // Pass the delete handler
                task={editingTask}
            />
        </div>
    );
};

export default KanbanBoardPage;