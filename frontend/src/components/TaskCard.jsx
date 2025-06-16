import React from 'react';

const AssigneeAvatar = ({ user }) => (
    <div 
        className="w-8 h-8 bg-neutral-700 rounded-full flex items-center justify-center text-xs font-bold text-white ring-2 ring-neutral-800 uppercase" 
        title={`${user.first_name} ${user.last_name}`}
    >
        {user.avatar_url ? (
            <img src={`http://localhost:8000/${user.avatar_url}`} alt="avatar" className="w-full h-full rounded-full object-cover" />
        ) : (
            `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`
        )}
    </div>
);


const TaskCard = ({ task, provided, onClick }) => (
    <div
        ref={provided.innerRef}
        {...provided.draggableProps}
        {...provided.dragHandleProps}
        onClick={onClick}
        className="bg-neutral-800 p-4 mb-4 rounded-lg shadow-md border border-neutral-700 hover:border-indigo-500 transition-colors duration-200 cursor-pointer"
    >
        <h4 className="font-semibold text-neutral-200">{task.title}</h4>
        <div className="flex justify-between items-end mt-4">
            <span className="text-xs font-medium bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded-full">{task.type}</span>
            <div className="flex -space-x-3">
                 {task.assignees.length > 0 ? (
                     task.assignees.map(user => <AssigneeAvatar key={user.id} user={user} />)
                 ) : (
                      <div className="w-8 h-8 border-2 border-dashed border-neutral-600 rounded-full flex items-center justify-center text-xs font-bold text-neutral-500" title="No assignees">?</div>
                 )}
            </div>
        </div>
    </div>
);

export default TaskCard;