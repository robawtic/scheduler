export interface Employee {
    id: string;
    employee_id: string;
    first_name: string;
    last_name: string;
    team_id: number;
    is_active: boolean;
}

export interface Qualification {
    name: string;
    level: number;
    acquired_date: string;
    expires_at?: string;
}

export interface Workstation {
    id: string;
    station_id: string;
    name: string;
    team_id: number;
    line_type_id?: number;
    is_active: boolean;
    capacity: number;
    equipment_type?: string;
    location?: string;
    maintenance_schedule: Record<string, number>;
}

export interface RequiredQualification {
    name: string;
    minimum_level: number;
}

export interface Schedule {
    id: string;
    team_id: number;
    start_date: string;
    periods_per_day: number;
    assignments: ShiftAssignment[];
    is_published: boolean;
    version: number;
    created_at: string;
    updated_at: string;
}

export interface ShiftAssignment {
    id: string;
    employee_id: string;
    workstation_id: string;
    period: number;
    status: ShiftStatus;
    notes: string;
}

export enum ShiftStatus {
    SCHEDULED = "scheduled",
    IN_PROGRESS = "in_progress",
    COMPLETED = "completed",
    CANCELLED = "cancelled",
} 