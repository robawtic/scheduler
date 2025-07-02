import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { isAuthenticated } from '../services/api';

interface PrivateRouteProps {
    children: React.ReactNode;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
    const location = useLocation();
    
    if (!isAuthenticated()) {
        // Redirect to login page with the current location
        return <Navigate to="/login" state={{ from: location }} replace />;
    }
    
    return <>{children}</>;
};