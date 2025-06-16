import React from 'react';
import { Draggable } from '@hello-pangea/dnd';
import TaskCard from './TaskCard';


const KanbanColumn = ({ column, tasks, provided, onTaskClick }) => (
    // ИЗМЕНЕНО: Новый дизайн колонки
    <div className="bg-neutral-800/50 rounded-lg flex flex-col h-full">
        <h3 className="font-semibold text-lg p-4 text-neutral-300 tracking-wide border-b border-neutral-700">{column.title} <span className="text-sm text-neutral-500">{tasks.length}</span></h3>
        <Droppable droppableId={column.id} type="task">
            {(provided, snapshot) => (
                <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`p-4 flex-grow transition-colors duration-200 ${snapshot.isDraggingOver ? 'bg-indigo-900/20' : ''}`}
                >
                    {tasks.map((task, index) => (
                        <Draggable key={task.id} draggableId={task.id.toString()} index={index}>
                            {(provided) => (
                                <TaskCard
                                    task={task}
                                    provided={provided}
                                    onClick={() => onTaskClick(task)}
                                />
                            )}
                        </Draggable>
                    ))}
                    {provided.placeholder}
                </div>
            )}
        </Droppable>
    </div>
);



export default KanbanColumn;