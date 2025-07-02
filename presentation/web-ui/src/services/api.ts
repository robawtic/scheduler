import axios from 'axios';
import type { Employee, Schedule, ShiftStatus, Workstation } from '../types';

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080',
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // Include cookies in requests
});

// Add interceptor to include CSRF token and Authorization header
api.interceptors.request.use(config => {
    // Get CSRF token from cookie
    const csrfToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];

    // Include CSRF token in header for state-changing requests
    if (csrfToken && ['post', 'put', 'delete', 'patch'].includes(config.method || '')) {
        config.headers['x-csrf-token'] = csrfToken;
    }

    // Include Authorization header if access token exists
    const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (accessToken) {
        config.headers['Authorization'] = `Bearer ${accessToken}`;
    }

    return config;
});

// CSRF token endpoint
export const fetchCsrfToken = async (): Promise<void> => {
    await api.get('/api/v1/csrf-token');
    // The token is automatically set as a cookie by the server
};

// Authentication types
interface LoginCredentials {
    username: string;
    password: string;
}

interface RegistrationData {
    username: string;
    email: string;
    password: string;
    confirm_password: string;
}

interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_at: string;
}

// Authentication functions
export const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
        // Convert credentials to form data format required by OAuth2
        const formData = new URLSearchParams();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        const response = await api.post<TokenResponse>('/api/v1/auth/token', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });

        // Store tokens in localStorage
        localStorage.setItem(ACCESS_TOKEN_KEY, response.data.access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, response.data.refresh_token);
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
};

export const logout = (): void => {
    // Remove tokens from localStorage
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
};

export const register = async (userData: RegistrationData): Promise<any> => {
    try {
        const response = await api.post('/api/v1/auth/register', userData);
        return response.data;
    } catch (error: any) {
        if (error.response?.data?.detail) {
            throw new Error(error.response.data.detail);
        }
        throw new Error('Registration failed. Please try again later.');
    }
};

export const refreshToken = async (): Promise<void> => {
    try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await api.post<TokenResponse>('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
        });

        // Store new tokens
        localStorage.setItem(ACCESS_TOKEN_KEY, response.data.access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, response.data.refresh_token);
    } catch (error) {
        console.error('Token refresh failed:', error);
        // If refresh fails, log out the user
        logout();
        throw error;
    }
};

export const isAuthenticated = (): boolean => {
    return !!localStorage.getItem(ACCESS_TOKEN_KEY);
};

// Schedule endpoints
export const getSchedules = async (): Promise<Schedule[]> => {
    const response = await api.get('/api/v1/schedules');
    return response.data;
};

export const getSchedule = async (id: string): Promise<Schedule> => {
    const response = await api.get(`/api/v1/schedules/${id}`);
    return response.data;
};

export const createSchedule = async (data: {
    team_id: number;
    start_date: string;
    periods_per_day?: number;
}): Promise<Schedule> => {
    const response = await api.post('/api/v1/schedules', data);
    return response.data;
};

export const publishSchedule = async (id: string): Promise<void> => {
    await api.post(`/api/v1/schedules/${id}/publish`);
};

export const updateAssignmentStatus = async (
    scheduleId: string,
    assignmentId: string,
    status: ShiftStatus
): Promise<void> => {
    await api.post(`/api/v1/schedules/${scheduleId}/assignments/${assignmentId}/status`, { status });
};

// Employee endpoints
export const getEmployees = async (): Promise<Employee[]> => {
    const response = await api.get('/api/v1/employees');
    return response.data;
};

export const getEmployee = async (id: string): Promise<Employee> => {
    const response = await api.get(`/api/v1/employees/${id}`);
    return response.data;
};

// Workstation endpoints
export const getWorkstations = async (): Promise<Workstation[]> => {
    const response = await api.get('/api/v1/workstations');
    return response.data;
};

export const getWorkstation = async (id: string): Promise<Workstation> => {
    const response = await api.get(`/api/v1/workstations/${id}`);
    return response.data;
};
