import React from 'react';
import { Toaster as HotToaster } from 'react-hot-toast'; // Renamed to HotToaster to avoid conflict if any
import { useTheme } from '../context/ThemeContext';

const AppToaster = () => {
  const { theme } = useTheme(); // Get current theme

  return (
    <HotToaster
      position="top-right"
      reverseOrder={false}
      toastOptions={{
        style: {
          background: theme === 'dark' ? '#333' : '#fff', // Dark grey for dark, white for light
          color: theme === 'dark' ? '#fff' : '#000',      // White text for dark, black for light
          border: theme === 'dark' ? '1px solid #555' : '1px solid #ddd', // Optional border
        },
        success: {
          style: {
            // Example: Greenish background for success (optional, can be customized further)
            // background: theme === 'dark' ? '#28a745' : '#d4edda', 
            // color: theme === 'dark' ? '#fff' : '#155724',
          },
        },
        error: {
          style: {
            // Example: Reddish background for error (optional, can be customized further)
            // background: theme === 'dark' ? '#dc3545' : '#f8d7da',
            // color: theme === 'dark' ? '#fff' : '#721c24',
          },
        },
      }}
    />
  );
};

export default AppToaster;
