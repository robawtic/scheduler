import React from 'react';
import {
    Drawer,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Divider,
    ListItemButton,
} from '@mui/material';
import {
    Schedule as ScheduleIcon,
    People as PeopleIcon,
    Business as BusinessIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface SidebarProps {
    open: boolean;
    onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
    const navigate = useNavigate();

    const menuItems = [
        { text: 'Schedules', icon: <ScheduleIcon />, path: '/schedules' },
        { text: 'Employees', icon: <PeopleIcon />, path: '/employees' },
        { text: 'Workstations', icon: <BusinessIcon />, path: '/workstations' },
    ];

    return (
        <Drawer
            variant="temporary"
            anchor="left"
            open={open}
            onClose={onClose}
            sx={{
                width: 240,
                flexShrink: 0,
                '& .MuiDrawer-paper': {
                    width: 240,
                    boxSizing: 'border-box',
                },
            }}
        >
            <List>
                {menuItems.map((item) => (
                    <ListItem key={item.text} disablePadding>
                        <ListItemButton
                            onClick={() => {
                                navigate(item.path);
                                onClose();
                            }}
                        >
                            <ListItemIcon>{item.icon}</ListItemIcon>
                            <ListItemText primary={item.text} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
            <Divider />
        </Drawer>
    );
}; 