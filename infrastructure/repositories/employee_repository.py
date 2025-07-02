from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.employee import Employee
from domain.repositories.employee_repository import EmployeeRepository
from infrastructure.models.employee import EmployeeModel

class SQLAlchemyEmployeeRepository(EmployeeRepository):
    """SQLAlchemy implementation of the employee repository."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, employee_id: UUID) -> Optional[Employee]:
        """Get an employee by ID."""
        model = self.session.query(EmployeeModel).filter_by(id=employee_id).first()
        return self._to_domain_entity(model) if model else None

    def get_by_team(self, team_id: int) -> List[Employee]:
        """Get all employees in a team."""
        models = self.session.query(EmployeeModel).filter_by(team_id=team_id).all()
        return [self._to_domain_entity(model) for model in models]

    def get_available_employees(self, date: datetime) -> List[Employee]:
        """Get all employees available on a given date."""
        # TODO: Implement availability check
        models = self.session.query(EmployeeModel).filter_by(is_active=True).all()
        return [self._to_domain_entity(model) for model in models]

    def save(self, employee: Employee) -> None:
        """Save or update an employee."""
        model = self.session.query(EmployeeModel).filter_by(id=employee.id).first()
        if not model:
            model = EmployeeModel()
        
        # Update model attributes
        for key, value in {
            'id': employee.id,
            'employee_id': employee.employee_id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'team_id': employee.team_id,
            'is_active': employee.is_active,
        }.items():
            setattr(model, key, value)
        
        self.session.add(model)
        self.session.commit()

    def get_all(self) -> List[Employee]:
        """Get all employees."""
        models = self.session.query(EmployeeModel).all()
        return [self._to_domain_entity(model) for model in models]

    def delete(self, employee_id: UUID) -> None:
        """Delete an employee."""
        self.session.query(EmployeeModel).filter_by(id=employee_id).delete()
        self.session.commit()

    def _to_domain_entity(self, model: EmployeeModel) -> Employee:
        """Convert ORM model to domain entity."""
        employee = Employee(
            employee_id=getattr(model, 'employee_id'),
            first_name=getattr(model, 'first_name'),
            last_name=getattr(model, 'last_name'),
            team_id=getattr(model, 'team_id'),
            is_active=getattr(model, 'is_active'),
        )
        employee.id = getattr(model, 'id')
        return employee 