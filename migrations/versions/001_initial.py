"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2023-11-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create schedules table
    op.create_table(
        'schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('periods_per_day', sa.Integer(), nullable=False, default=4),
        sa.Column('is_published', sa.Boolean(), default=False),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_schedules_team_id', 'schedules', ['team_id'])
    op.create_index('ix_schedules_start_date', 'schedules', ['start_date'])

    # Create shift_assignments table
    op.create_table(
        'shift_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('schedule_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workstation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('period', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='scheduled'),
        sa.Column('notes', sa.String()),
        sa.ForeignKeyConstraint(['schedule_id'], ['schedules.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_shift_assignments_schedule_id', 'shift_assignments', ['schedule_id'])
    op.create_index('ix_shift_assignments_employee_id', 'shift_assignments', ['employee_id'])
    op.create_index('ix_shift_assignments_workstation_id', 'shift_assignments', ['workstation_id'])


def downgrade() -> None:
    op.drop_table('shift_assignments')
    op.drop_table('schedules') 