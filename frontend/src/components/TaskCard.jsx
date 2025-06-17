import React, { memo } from 'react';

const AssigneeAvatar = ({ user }) => (
    <div
        className="w-8 h-8 bg-neutral-300 dark:bg-neutral-700 rounded-full flex items-center justify-center text-xs font-bold text-neutral-700 dark:text-white ring-2 ring-white dark:ring-neutral-800 uppercase"
        title={`${user.first_name} ${user.last_name}`}
    >
        {user.avatar_url ? (
            <img src={`http://localhost:8000/api/${user.avatar_url}?v=${user.avatar_last_updated || '0'}`} alt="avatar" className="w-full h-full rounded-full object-cover" />
        ) : (
            `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`
        )}
    </div>
);
const MemoizedAssigneeAvatar = memo(AssigneeAvatar);


const TaskCard = ({ task, provided, onClick, onDelete }) => { // Added onDelete prop
    const handleDeleteClick = (event) => {
        event.stopPropagation(); // Prevent card's onClick from firing
        if (onDelete) {
            onDelete(task.id, task.title); // MODIFIED: Pass task.id and task.title
        }
    };

    return (
        <div
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            onClick={onClick}
            className="relative bg-white dark:bg-neutral-800 p-4 mb-4 rounded-lg shadow-md dark:shadow-lg border border-neutral-200 dark:border-neutral-700 hover:border-indigo-500 dark:hover:border-indigo-500 transition-colors duration-200 cursor-pointer"
        >
            {/* Delete Button */}
            {onDelete && ( // Render button only if onDelete is provided
                <button
                    onClick={handleDeleteClick}
                    className="absolute top-2 right-2 text-xs text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-600 px-2 py-1 bg-red-100 dark:bg-red-700/30 rounded hover:bg-red-200 dark:hover:bg-red-600/50 transition-colors"
                    aria-label="Delete task"
                >
                    Delete
                </button>
            )}

            <h4 className="font-semibold text-neutral-700 dark:text-neutral-200 mb-2 pr-10">{task.title}</h4> {/* Added pr-10 to avoid overlap with delete button */}
            <div className="flex justify-between items-center mb-2">
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${task.type === 'task' ? 'bg-sky-100 dark:bg-sky-500/20 text-sky-700 dark:text-sky-300' : 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300'}`}>{task.type}</span>
                <span
                className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                    task.priority === 'high' ? 'bg-red-100 text-red-700 dark:bg-red-700/30 dark:text-red-300' :
                    task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-700/30 dark:text-yellow-300' :
                    task.priority === 'low' ? 'bg-green-100 text-green-700 dark:bg-green-700/30 dark:text-green-300' :
                    'bg-gray-100 text-gray-700 dark:bg-gray-700/30 dark:text-gray-300' // Default fallback
                }`}
            >
                {task.priority ? task.priority.charAt(0).toUpperCase() + task.priority.slice(1) : 'N/A'}
            </span>
        </div>
        <div className="flex justify-between items-end">
            {/* Assignee avatars will go here, but they are on a new line if the title is long, let's keep them at the bottom */}
            <div></div> {/* Empty div to push assignees to the right if needed, or adjust main flex container */}
            <div className="flex -space-x-3">
                 {task.assignees.length > 0 ? (
                     task.assignees.slice(0, 3).map(user => <MemoizedAssigneeAvatar key={user.id} user={user} />)
                 ) : (
                      <div className="w-8 h-8 border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-full flex items-center justify-center text-xs font-bold text-neutral-400 dark:text-neutral-500" title="No assignees">?</div>
                 )}
                 {task.assignees.length > 3 && (
                    <div className="w-8 h-8 bg-neutral-300 dark:bg-neutral-600 rounded-full flex items-center justify-center text-xs font-bold text-neutral-700 dark:text-white ring-2 ring-white dark:ring-neutral-800">
                        +{task.assignees.length - 3}
                    </div>
                 )}
            </div>
        </div>
    </div>
);
}

export default memo(TaskCard);