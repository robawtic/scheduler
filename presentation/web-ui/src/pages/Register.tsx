import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    Box, 
    Button, 
    TextField, 
    Typography, 
    Paper, 
    Container,
    Alert,
    Link
} from '@mui/material';
import { RegisterForm } from '../components/RegisterForm';

export const Register: React.FC = () => {
    return (
        <Container maxWidth="sm">
            <Box sx={{ mt: 8 }}>
                <Paper elevation={3} sx={{ p: 4 }}>
                    <Typography component="h1" variant="h5" align="center" gutterBottom>
                        Create an Account
                    </Typography>
                    
                    <RegisterForm />
                    
                    <Box sx={{ mt: 2, textAlign: 'center' }}>
                        <Typography variant="body2">
                            Already have an account?{' '}
                            <Link href="/login" underline="hover">
                                Sign in
                            </Link>
                        </Typography>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default Register;