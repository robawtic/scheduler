import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
    AppBar as MuiAppBar,
    Toolbar,
    Typography,
    IconButton,
    Box,
    Button,
} from '@mui/material';
import { Menu as MenuIcon, Logout as LogoutIcon } from '@mui/icons-material';
import { logout, isAuthenticated } from '../../services/api';

interface AppBarProps {
    onMenuClick: () => void;
}

export const AppBar: React.FC<AppBarProps> = ({ onMenuClick }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <MuiAppBar position="fixed">
            <Toolbar>
                <IconButton
                    color="inherit"
                    aria-label="open drawer"
                    edge="start"
                    onClick={onMenuClick}
                    sx={{ mr: 2 }}
                >
                    <MenuIcon />
                </IconButton>
                <Typography variant="h6" noWrap component="div">
                    Heijunka Scheduler
                </Typography>
                <Box sx={{ flexGrow: 1 }} />

                {isAuthenticated() && (
                    <Button 
                        color="inherit" 
                        onClick={handleLogout}
                        startIcon={<LogoutIcon />}
                    >
                        Logout
                    </Button>
                )}
            </Toolbar>
        </MuiAppBar>
    );
};
