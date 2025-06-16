import React from 'react';
import { Droppable, Draggable } from '@hello-pangea/dnd';
import TaskCard from './TaskCard';

const KanbanColumn = ({ column, tasks, onTaskClick }) => (
    <div className="bg-neutral-800/50 rounded-lg flex flex-col h-full w-full">
        <h3 className="font-semibold text-lg p-4 text-neutral-300 tracking-wide border-b border-neutral-700 flex-shrink-0">
            {column.title}
            <span className="text-sm text-neutral-500 ml-2">{tasks.length}</span>
        </h3>
        <Droppable droppableId={column.id}>
            {(provided, snapshot) => (
                <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`p-4 flex-grow transition-colors duration-200 ${snapshot.isDraggingOver ? 'bg-indigo-900/10' : ''}`}
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