import React from 'react';
import {
    Box,
    Button,
    FormControl,
    FormHelperText,
    InputLabel,
    MenuItem,
    Select,
    Typography,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers';
import { Controller, useForm } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { getEmployees, getWorkstations } from '../../services/api';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { addDays, isWeekend } from 'date-fns';

const scheduleFormSchema = z.object({
    team_id: z.number().min(1, 'Team is required'),
    start_date: z.date()
        .refine((date: Date) => !isWeekend(date), {
            message: 'Start date must be a weekday',
        })
        .refine((date: Date) => date >= addDays(new Date(), -1), {
            message: 'Start date cannot be in the past',
        }),
    periods_per_day: z.number().min(2).max(6),
});

type ScheduleFormData = z.infer<typeof scheduleFormSchema>;

interface ScheduleFormProps {
    onSubmit: (data: ScheduleFormData) => void;
    isLoading?: boolean;
}

export const ScheduleForm: React.FC<ScheduleFormProps> = ({
    onSubmit,
    isLoading = false,
}) => {
    // Fetch teams data
    const { data: employees } = useQuery({
        queryKey: ['employees'],
        queryFn: getEmployees,
    });

    // Get unique team IDs from employees
    const teams = React.useMemo(() => {
        if (!employees) return [];
        const teamIds = [...new Set(employees.map(e => e.team_id))];
        return teamIds.sort((a, b) => a - b);
    }, [employees]);

    const {
        control,
        handleSubmit,
        formState: { errors },
    } = useForm<ScheduleFormData>({
        resolver: zodResolver(scheduleFormSchema),
        defaultValues: {
            team_id: 1,
            start_date: new Date(),
            periods_per_day: 4,
        },
    });

    return (
        <Box
            component="form"
            onSubmit={handleSubmit(onSubmit)}
            sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                maxWidth: 400,
                margin: '0 auto',
                mt: 2,
            }}
        >
            <Typography variant="h6" gutterBottom>
                Generate New Schedule
            </Typography>

            <Controller
                name="team_id"
                control={control}
                render={({ field }) => (
                    <FormControl fullWidth error={!!errors.team_id}>
                        <InputLabel>Team</InputLabel>
                        <Select {...field} label="Team">
                            {teams.map((teamId: number) => (
                                <MenuItem key={teamId} value={teamId}>
                                    Team {teamId}
                                </MenuItem>
                            ))}
                        </Select>
                        {errors.team_id && (
                            <FormHelperText>{errors.team_id.message}</FormHelperText>
                        )}
                    </FormControl>
                )}
            />

            <Controller
                name="start_date"
                control={control}
                render={({ field }) => (
                    <DatePicker
                        label="Start Date"
                        value={field.value}
                        onChange={field.onChange}
                        slotProps={{
                            textField: {
                                fullWidth: true,
                                error: !!errors.start_date,
                                helperText: errors.start_date?.message,
                            },
                        }}
                        disablePast
                        shouldDisableDate={isWeekend}
                    />
                )}
            />

            <Controller
                name="periods_per_day"
                control={control}
                render={({ field }) => (
                    <FormControl fullWidth error={!!errors.periods_per_day}>
                        <InputLabel>Periods Per Day</InputLabel>
                        <Select {...field} label="Periods Per Day">
                            {[2, 3, 4, 5, 6].map((value: number) => (
                                <MenuItem key={value} value={value}>
                                    {value} Periods
                                </MenuItem>
                            ))}
                        </Select>
                        {errors.periods_per_day && (
                            <FormHelperText>{errors.periods_per_day.message}</FormHelperText>
                        )}
                    </FormControl>
                )}
            />

            <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={isLoading}
                sx={{ mt: 2 }}
            >
                {isLoading ? 'Generating Schedule...' : 'Generate Schedule'}
            </Button>
        </Box>
    );
}; 