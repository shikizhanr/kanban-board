import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import './index.css'; // Для стилей Tailwind
import { ThemeProvider } from './context/ThemeContext.jsx'; // Import ThemeProvider
import AppToaster from './components/AppToaster.jsx'; // Import the new AppToaster

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider> {/* Wrap App with ThemeProvider */}
        <App />
        <AppToaster /> {/* Use the new theme-aware AppToaster */}
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);