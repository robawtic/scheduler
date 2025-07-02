from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.models.Base import Base
from domain.models.DepartmentModel import DepartmentModel
from domain.models.GroupModel import GroupModel
from domain.models.TeamModel import TeamModel
from domain.models.EmployeeModel import EmployeeModel
from domain.models.WorkstationModel import WorkstationModel
from domain.models.RoleModel import RoleModel
from domain.models.TeamMemberModel import TeamMemberModel

# Create database connection
engine = create_engine('sqlite:///scheduler.db')
Session = sessionmaker(bind=engine)
session = Session()

def setup_initial_data():
    try:
        # Create all tables
        Base.metadata.create_all(engine)

        # Create Department
        powertrain = DepartmentModel(
            name='powertrain',
            description='Powertrain Assembly Department'
        )
        session.add(powertrain)
        session.flush()  # Flush to get the department ID

        # Create Group
        shortblock_group = GroupModel(
            name='shortblock',
            department_id=powertrain.id
        )
        session.add(shortblock_group)
        session.flush()  # Flush to get the group ID

        # Create Teams
        teams = [
            TeamModel(name='headsub', description='Head Sub-Assembly Team', group_id=shortblock_group.id),
            TeamModel(name='camsub', description='Camshaft Sub-Assembly Team', group_id=shortblock_group.id),
            TeamModel(name='shortblock', description='Short Block Assembly Team', group_id=shortblock_group.id)
        ]
        session.add_all(teams)
        session.flush()  # Flush to get team IDs

        # Create Roles
        roles = [
            RoleModel(name='Team Lead', description='Team Leader'),
            RoleModel(name='Operator', description='Machine Operator'),
            RoleModel(name='Inspector', description='Quality Inspector')
        ]
        session.add_all(roles)
        session.flush()

        # Create Employees and Team Members for each team
        for team in teams:
            # Create 5 employees per team
            for i in range(5):
                employee = EmployeeModel(
                    employee_id=f'{team.name}_{i+1}',
                    first_name=f'Employee{i+1}',
                    last_name=f'{team.name.capitalize()}',
                    team_id=team.id,
                    is_active=True
                )
                session.add(employee)
                session.flush()

                # Assign roles
                role = roles[1] if i > 0 else roles[0]  # First employee is team lead, others are operators
                team_member = TeamMemberModel(
                    employee_id=employee.id,
                    team_id=team.id,
                    role_id=role.id
                )
                session.add(team_member)

            # Create workstations for each team
            workstations = []
            if team.name == 'headsub':
                workstations = [
                    ('HS1', 'Valve Guide Press'),
                    ('HS2', 'Valve Seat Machine'),
                    ('HS3', 'Head Assembly Station'),
                    ('HS4', 'Quality Check Station')
                ]
            elif team.name == 'camsub':
                workstations = [
                    ('CS1', 'Cam Bearing Press'),
                    ('CS2', 'Cam Assembly Station'),
                    ('CS3', 'Timing Component Assembly'),
                    ('CS4', 'Quality Check Station')
                ]
            else:  # shortblock
                workstations = [
                    ('SB1', 'Block Cleaning Station'),
                    ('SB2', 'Piston Assembly'),
                    ('SB3', 'Crankshaft Installation'),
                    ('SB4', 'Final Assembly Station'),
                    ('SB5', 'Quality Check Station')
                ]

            for station_id, name in workstations:
                workstation = WorkstationModel(
                    station_id=station_id,
                    name=name,
                    team_id=team.id,
                    is_active=True,
                    capacity=1,
                    equipment_type='Assembly Station',
                    location=f'{team.name.upper()} Area'
                )
                session.add(workstation)

        # Commit all changes
        session.commit()
        print("Initial data setup completed successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error setting up initial data: {e}")
        raise

if __name__ == '__main__':
    setup_initial_data() 