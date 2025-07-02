import React, { useState } from 'react';
import { Box, CssBaseline, Toolbar } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { AppBar } from './AppBar';
import { Sidebar } from './Sidebar';

interface LayoutProps {
    children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const location = useLocation();

    // Check if we're on the login page
    const isLoginPage = location.pathname === '/login';

    const handleSidebarToggle = () => {
        setSidebarOpen(!sidebarOpen);
    };

    // For login page, render without navigation elements
    if (isLoginPage) {
        return (
            <Box sx={{ display: 'flex' }}>
                <CssBaseline />
                <Box
                    component="main"
                    sx={{
                        flexGrow: 1,
                        width: '100%',
                        minHeight: '100vh',
                        backgroundColor: (theme) => theme.palette.grey[100],
                    }}
                >
                    {children}
                </Box>
            </Box>
        );
    }

    // For authenticated pages, render with navigation
    return (
        <Box sx={{ display: 'flex' }}>
            <CssBaseline />
            <AppBar onMenuClick={handleSidebarToggle} />
            <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    p: 3,
                    width: '100%',
                    minHeight: '100vh',
                    backgroundColor: (theme) => theme.palette.grey[100],
                }}
            >
                <Toolbar />
                {children}
            </Box>
        </Box>
    );
};
