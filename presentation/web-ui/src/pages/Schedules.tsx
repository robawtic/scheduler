import React, { useState } from 'react';
import {
    Alert,
    Box,
    Button,
    Container,
    Dialog,
    DialogContent,
    DialogTitle,
    Grid,
    Paper,
    Snackbar,
    Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format, parseISO } from 'date-fns';

import { ScheduleGrid } from '../components/Schedule/ScheduleGrid';
import { ScheduleForm } from '../components/Schedule/ScheduleForm';
import { createSchedule, getSchedule, getSchedules, updateAssignmentStatus } from '../services/api';
import type { Schedule, ShiftStatus } from '../types';

type CreateScheduleData = {
    team_id: number;
    start_date: Date;
    periods_per_day: number;
};

type UpdateAssignmentData = {
    scheduleId: string;
    assignmentId: string;
    status: ShiftStatus;
};

export const Schedules: React.FC = () => {
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [selectedSchedule, setSelectedSchedule] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const queryClient = useQueryClient();

    // Fetch all schedules
    const { data: schedules = [] } = useQuery({
        queryKey: ['schedules'],
        queryFn: getSchedules,
    });

    // Fetch selected schedule
    const { data: schedule, isLoading } = useQuery({
        queryKey: ['schedule', selectedSchedule],
        queryFn: () => getSchedule(selectedSchedule!),
        enabled: !!selectedSchedule,
    });

    // Create schedule mutation
    const createMutation = useMutation<Schedule, Error, CreateScheduleData>({
        mutationFn: (data) => createSchedule({
            ...data,
            start_date: format(data.start_date, 'yyyy-MM-dd'),
        }),
        onSuccess: (newSchedule) => {
            queryClient.invalidateQueries({ queryKey: ['schedules'] });
            setSelectedSchedule(newSchedule.id);
            setCreateDialogOpen(false);
        },
        onError: (error) => {
            setError(`Failed to create schedule: ${error.message}`);
        },
    });

    // Update assignment status mutation
    const updateStatusMutation = useMutation<void, Error, UpdateAssignmentData>({
        mutationFn: ({ scheduleId, assignmentId, status }) =>
            updateAssignmentStatus(scheduleId, assignmentId, status),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['schedule', selectedSchedule] });
        },
        onError: (error) => {
            setError(`Failed to update status: ${error.message}`);
        },
    });

    const handleCreateSchedule = (data: CreateScheduleData) => {
        createMutation.mutate(data);
    };

    const handleStatusChange = (assignmentId: string, status: ShiftStatus) => {
        if (selectedSchedule) {
            updateStatusMutation.mutate({
                scheduleId: selectedSchedule,
                assignmentId,
                status,
            });
        }
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h4" component="h1">
                    Schedules
                </Typography>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => setCreateDialogOpen(true)}
                >
                    Create Schedule
                </Button>
            </Box>

            <Box sx={{ display: 'flex', gap: 3 }}>
                {/* Schedule List */}
                <Box sx={{ width: '25%', minWidth: 250 }}>
                    <Paper sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>
                            Recent Schedules
                        </Typography>
                        {schedules.length === 0 ? (
                            <Typography variant="body2" color="text.secondary">
                                No schedules found
                            </Typography>
                        ) : (
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                {schedules.map((s) => (
                                    <Button
                                        key={s.id}
                                        variant={selectedSchedule === s.id ? 'contained' : 'outlined'}
                                        onClick={() => setSelectedSchedule(s.id)}
                                        sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
                                    >
                                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                                            <Typography variant="subtitle2">
                                                Team {s.team_id}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                {format(parseISO(s.start_date), 'MMM d, yyyy')}
                                            </Typography>
                                        </Box>
                                    </Button>
                                ))}
                            </Box>
                        )}
                    </Paper>
                </Box>

                {/* Schedule Grid */}
                <Box sx={{ flex: 1 }}>
                    <Paper sx={{ p: 2 }}>
                        {schedule ? (
                            <ScheduleGrid schedule={schedule} onStatusChange={handleStatusChange} />
                        ) : (
                            <Typography variant="body1" sx={{ textAlign: 'center', py: 4 }}>
                                {isLoading ? 'Loading schedule...' : 'Select or create a schedule to view'}
                            </Typography>
                        )}
                    </Paper>
                </Box>
            </Box>

            <Dialog
                open={createDialogOpen}
                onClose={() => setCreateDialogOpen(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>Create New Schedule</DialogTitle>
                <DialogContent>
                    <ScheduleForm
                        onSubmit={handleCreateSchedule}
                        isLoading={createMutation.isPending}
                    />
                </DialogContent>
            </Dialog>

            <Snackbar
                open={!!error}
                autoHideDuration={6000}
                onClose={() => setError(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert onClose={() => setError(null)} severity="error">
                    {error}
                </Alert>
            </Snackbar>
        </Container>
    );
}; 