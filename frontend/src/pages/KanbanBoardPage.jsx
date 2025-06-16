import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable } from '@hello-pangea/dnd';
import api from '../api';
import useAuth from '../hooks/useAuth';
import KanbanColumn from '../components/KanbanColumn';
import Spinner from '../components/Spinner';

const KanbanBoardPage = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { logout } = useAuth();

    const columns = {
        todo: { id: 'todo', title: 'Запланировано' },
        in_progress: { id: 'in_progress', title: 'В работе' },
        done: { id: 'done', title: 'Готово' },
    };

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                const response = await api.get('/tasks/');
                setTasks(response.data);
            } catch (err) {
                setError('Не удалось загрузить задачи.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchTasks();
    }, []);

    const onDragEnd = async (result) => {
        const { source, destination, draggableId } = result;
        if (!destination || (source.droppableId === destination.droppableId && source.index === destination.index)) {
            return;
        }

        const taskId = parseInt(draggableId);
        const newStatus = destination.droppableId;
        const taskToMove = tasks.find(t => t.id === taskId);

        // Оптимистичное обновление UI
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
            setTasks(currentTasks); // Откатываем UI в случае ошибки
        }
    };

    if (loading) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }
    if (error) {
        return <div className="text-center text-red-500 mt-10">{error}</div>;
    }

    return (
        <div className="flex flex-col h-screen bg-gray-50 font-sans">
            <header className="bg-white shadow-md p-4 flex justify-between items-center flex-shrink-0">
                <h1 className="text-2xl font-bold text-indigo-600">Kanban.PRO</h1>
                <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 text-sm font-semibold">Выйти</button>
            </header>
            <main className="flex-grow p-4 overflow-x-auto">
                <DragDropContext onDragEnd={onDragEnd}>
                    <div className="flex space-x-4">
                        {Object.values(columns).map(column => {
                            const columnTasks = tasks.filter(task => task.status === column.id);
                            return (
                                <Droppable key={column.id} droppableId={column.id}>
                                    {(provided) => (
                                        <KanbanColumn column={column} tasks={columnTasks} provided={provided} />
                                    )}
                                </Droppable>
                            );
                        })}
                    </div>
                </DragDropContext>
            </main>
        </div>
    );
};

export default KanbanBoardPage;