import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import { Layout } from './components/Layout/Layout';
import { PrivateRoute } from './components/PrivateRoute';
import { Schedules } from './pages/Schedules';
import { Login } from './pages/Login';
import Register from './pages/Register';
import { fetchCsrfToken, isAuthenticated } from './services/api';

// Create a client for React Query
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
            retry: 1,
        },
    },
});

// Create theme
const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2',
        },
        secondary: {
            main: '#dc004e',
        },
        background: {
            default: '#f5f5f5',
        },
    },
    typography: {
        h1: {
            fontSize: '2.5rem',
            fontWeight: 500,
        },
        h2: {
            fontSize: '2rem',
            fontWeight: 500,
        },
        h3: {
            fontSize: '1.75rem',
            fontWeight: 500,
        },
        h4: {
            fontSize: '1.5rem',
            fontWeight: 500,
        },
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                },
            },
        },
    },
});

function App() {
    // Fetch CSRF token when the app starts
    useEffect(() => {
        fetchCsrfToken().catch(error => {
            console.error('Failed to fetch CSRF token:', error);
        });
    }, []);

    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <BrowserRouter>
                        <Layout>
                            <Routes>
                                <Route path="/login" element={<Login />} />
                                <Route path="/register" element={<Register />} />
                                <Route 
                                    path="/schedules" 
                                    element={
                                        <PrivateRoute>
                                            <Schedules />
                                        </PrivateRoute>
                                    } 
                                />
                                <Route 
                                    path="/" 
                                    element={
                                        isAuthenticated() ? 
                                            <Navigate to="/schedules" replace /> : 
                                            <Navigate to="/login" replace />
                                    } 
                                />
                            </Routes>
                        </Layout>
                    </BrowserRouter>
                </LocalizationProvider>
            </ThemeProvider>
        </QueryClientProvider>
    );
}

export default App;
