import React from 'react';

const TaskCard = ({ task, provided, onClick }) => (
    <div
        ref={provided.innerRef}
        {...provided.draggableProps}
        {...provided.dragHandleProps}
        onClick={onClick} // <-- Добавляем обработчик клика
        className="bg-white p-4 mb-4 rounded-lg shadow-md border-l-4 border-indigo-500 hover:shadow-lg transition-shadow duration-200 cursor-pointer" // <-- Меняем cursor-grab на cursor-pointer
    >
        <h4 className="font-semibold text-gray-800">{task.title}</h4>
        <p className="text-sm text-gray-600 mt-1">{task.description}</p>
        <div className="flex justify-between items-center mt-4">
            <span className="text-xs font-medium bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">{task.type}</span>
            <div className="flex -space-x-2">
                 {task.assignee ? (
                     <div className="w-7 h-7 bg-gray-700 rounded-full flex items-center justify-center text-xs font-bold text-white ring-2 ring-white uppercase" title={task.assignee.email}>
                         {task.assignee.first_name.charAt(0)}{task.assignee.last_name.charAt(0)}
                     </div>
                 ) : (
                      <div className="w-7 h-7 bg-gray-200 rounded-full flex items-center justify-center text-xs font-bold text-gray-400 ring-2 ring-white" title="No assignee">?</div>
                 )}
            </div>
        </div>
    </div>
);

export default TaskCard;