import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import KanbanBoardPage from './pages/KanbanBoardPage';

function App() {
    return (
        <AuthProvider>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <KanbanBoardPage />
                        </ProtectedRoute>
                    }
                />
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </AuthProvider>
    );
}

export default App;
