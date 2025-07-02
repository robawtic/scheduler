import React from 'react';
import type {
    DataGridProps,
    GridColDef,
    GridRenderCellParams,
} from '@mui/x-data-grid';
import { DataGrid } from '@mui/x-data-grid';
import { Chip, CircularProgress } from '@mui/material';
import {
    CheckCircle as CompletedIcon,
    Cancel as CancelledIcon,
    Schedule as ScheduledIcon,
    PlayArrow as InProgressIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import type { Schedule, ShiftAssignment } from '../../types';
import { ShiftStatus } from '../../types';
import { getEmployee, getWorkstation } from '../../services/api';

interface ScheduleGridProps {
    schedule: Schedule;
    onStatusChange: (assignmentId: string, status: ShiftStatus) => void;
}

const statusIcons = {
    [ShiftStatus.SCHEDULED]: <ScheduledIcon color="info" />,
    [ShiftStatus.IN_PROGRESS]: <InProgressIcon color="warning" />,
    [ShiftStatus.COMPLETED]: <CompletedIcon color="success" />,
    [ShiftStatus.CANCELLED]: <CancelledIcon color="error" />,
};

export const ScheduleGrid: React.FC<ScheduleGridProps> = ({
    schedule,
    onStatusChange,
}) => {
    // Create a map of unique employee IDs
    const employeeIds = [...new Set(schedule.assignments.map(a => a.employee_id))];
    const workstationIds = [...new Set(schedule.assignments.map(a => a.workstation_id))];

    // Fetch employee data
    const { data: employees } = useQuery({
        queryKey: ['employees', employeeIds],
        queryFn: async () => {
            const promises = employeeIds.map(id => getEmployee(id));
            const results = await Promise.all(promises);
            return Object.fromEntries(results.map(e => [e.id, e]));
        },
    });

    // Fetch workstation data
    const { data: workstations } = useQuery({
        queryKey: ['workstations', workstationIds],
        queryFn: async () => {
            const promises = workstationIds.map(id => getWorkstation(id));
            const results = await Promise.all(promises);
            return Object.fromEntries(results.map(w => [w.id, w]));
        },
    });

    const columns: GridColDef[] = [
        {
            field: 'period',
            headerName: 'Period',
            width: 100,
        },
        {
            field: 'employee',
            headerName: 'Employee',
            width: 200,
            valueGetter: ({ row }) => {
                const assignment = row as ShiftAssignment;
                const employee = employees?.[assignment.employee_id];
                return employee ? `${employee.first_name} ${employee.last_name}` : assignment.employee_id;
            },
        },
        {
            field: 'workstation',
            headerName: 'Workstation',
            width: 200,
            valueGetter: ({ row }) => {
                const assignment = row as ShiftAssignment;
                const workstation = workstations?.[assignment.workstation_id];
                return workstation ? workstation.name : assignment.workstation_id;
            },
        },
        {
            field: 'status',
            headerName: 'Status',
            width: 150,
            renderCell: ({ row }) => {
                const assignment = row as ShiftAssignment;
                return (
                    <Chip
                        icon={statusIcons[assignment.status]}
                        label={assignment.status}
                        variant="outlined"
                        color={
                            assignment.status === ShiftStatus.COMPLETED
                                ? 'success'
                                : assignment.status === ShiftStatus.CANCELLED
                                ? 'error'
                                : assignment.status === ShiftStatus.IN_PROGRESS
                                ? 'warning'
                                : 'info'
                        }
                        onClick={() => {
                            // Cycle through statuses
                            const statuses = Object.values(ShiftStatus);
                            const currentIndex = statuses.indexOf(assignment.status);
                            const nextStatus = statuses[(currentIndex + 1) % statuses.length];
                            onStatusChange(assignment.id, nextStatus);
                        }}
                    />
                );
            },
        },
        {
            field: 'notes',
            headerName: 'Notes',
            width: 300,
        },
    ];

    if (!employees || !workstations) {
        return <CircularProgress />;
    }

    return (
        <DataGrid
            rows={schedule.assignments}
            columns={columns}
            initialState={{
                pagination: {
                    paginationModel: {
                        pageSize: 10,
                    },
                },
            }}
            pageSizeOptions={[10, 25, 50]}
            autoHeight
            disableRowSelectionOnClick
            getRowId={(row) => row.id}
            sx={{
                backgroundColor: 'white',
                '& .MuiDataGrid-cell:focus': {
                    outline: 'none',
                },
            }}
        />
    );
}; 