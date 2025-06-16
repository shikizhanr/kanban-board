import React from 'react';
import { Draggable } from '@hello-pangea/dnd';
import TaskCard from './TaskCard';

const KanbanColumn = ({ column, tasks, provided }) => (
    <div
        {...provided.droppableProps}
        ref={provided.innerRef}
        className="bg-gray-100 rounded-lg p-4 w-80 flex-shrink-0"
    >
        <h3 className="font-bold text-lg mb-4 text-gray-700 tracking-wide">{column.title}</h3>
        <div className="min-h-[200px]">
            {tasks.map((task, index) => (
                <Draggable key={task.id} draggableId={task.id.toString()} index={index}>
                    {(provided) => (
                        <TaskCard task={task} provided={provided} />
                    )}
                </Draggable>
            ))}
            {provided.placeholder}
        </div>
    </div>
);

export default KanbanColumn;
