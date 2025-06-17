import React from 'react';
import { useTheme } from '../context/ThemeContext';

const ThemeToggleButton = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-neutral-700 hover:bg-neutral-600 text-sm font-semibold text-white transition-colors"
        >
            {theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
        </button>
    );
};

export default ThemeToggleButton;
