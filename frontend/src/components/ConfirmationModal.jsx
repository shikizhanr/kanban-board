import React from 'react';

const ConfirmationModal = ({ isOpen, onClose, onConfirm, title, message, confirmButtonText = 'Confirm', cancelButtonText = 'Cancel', confirmButtonColor = 'red' }) => {
    if (!isOpen) return null;

    const confirmColorClasses = {
        red: 'bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-600',
        indigo: 'bg-indigo-600 hover:bg-indigo-700 dark:hover:bg-indigo-500',
        // Add other colors if needed
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex justify-center items-center z-[60] p-4 transition-opacity duration-300 ease-in-out"> {/* Higher z-index if needed */}
            <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-xl p-6 md:p-8 w-full max-w-md border border-neutral-200 dark:border-neutral-700 transform transition-all duration-300 ease-in-out scale-100">
                <h3 className="text-xl font-semibold mb-4 text-neutral-800 dark:text-neutral-100">{title}</h3>
                <p className="text-neutral-600 dark:text-neutral-300 mb-6 text-sm">{message}</p>
                <div className="flex justify-end space-x-4">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 bg-neutral-200 dark:bg-neutral-600 text-neutral-800 dark:text-neutral-100 rounded-lg hover:bg-neutral-300 dark:hover:bg-neutral-500 transition-colors"
                    >
                        {cancelButtonText}
                    </button>
                    <button
                        type="button"
                        onClick={onConfirm}
                        className={`px-4 py-2 text-white rounded-lg transition-colors ${confirmColorClasses[confirmButtonColor] || confirmColorClasses.indigo}`}
                    >
                        {confirmButtonText}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmationModal;
