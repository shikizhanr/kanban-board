import React, { useState, useEffect, useCallback } from 'react';
import { DragDropContext, Droppable } from '@hello-pangea/dnd';
import api from '../api';
import useAuth from '../hooks/useAuth';
import KanbanColumn from '../components/KanbanColumn';
import Spinner from '../components/Spinner';
import AddTaskModal from '../components/AddTaskModal';
import EditTaskModal from '../components/EditTaskModal'; // <-- 1. Импортируем новое окно

const KanbanBoardPage = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { logout } = useAuth();
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    
    // 2. Добавляем состояние для окна редактирования
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

    // 3. Функция для обновления задачи в списке после редактирования
    const handleTaskUpdated = (updatedTask) => {
        setTasks(prevTasks => prevTasks.map(task => 
            task.id === updatedTask.id ? updatedTask : task
        ));
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

    if (loading) return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    if (error) return <div className="text-center text-red-500 mt-10">{error}</div>;

    return (
        <div className="flex flex-col h-screen bg-gray-50 font-sans">
            <header className="bg-white shadow-md p-4 flex justify-between items-center flex-shrink-0">
                <h1 className="text-2xl font-bold text-indigo-600">Kanban.PRO</h1>
                <div className="flex items-center space-x-4">
                    <button 
                        onClick={() => setIsAddModalOpen(true)}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm font-semibold"
                    >
                        + Создать задачу
                    </button>
                    <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 text-sm font-semibold">Выйти</button>
                </div>
            </header>
            <main className="flex-grow p-4 overflow-x-auto">
                <DragDropContext onDragEnd={onDragEnd}>
                    <div className="flex space-x-4">
                        {Object.values(columns).map(column => {
                            const columnTasks = tasks.filter(task => task.status === column.id);
                            return (
                                <Droppable key={column.id} droppableId={column.id}>
                                    {(provided) => (
                                        <KanbanColumn 
                                            column={column} 
                                            tasks={columnTasks} 
                                            provided={provided}
                                            onTaskClick={(task) => setEditingTask(task)} // <-- 4. Передаем обработчик
                                        />
                                    )}
                                </Droppable>
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
            {/* 5. Рендерим модальное окно редактирования */}
            <EditTaskModal 
                isOpen={!!editingTask}
                onClose={() => setEditingTask(null)}
                onTaskUpdated={handleTaskUpdated}
                task={editingTask}
            />
        </div>
    );
};

export default KanbanBoardPage;
