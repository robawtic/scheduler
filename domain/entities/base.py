from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class Entity:
    """Base class for all domain entities."""
    
    def __init__(self, id: Optional[UUID] = None):
        self.id = id or uuid4()
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()

    def update(self) -> None:
        """Update the entity's last modified timestamp."""
        self.updated_at = datetime.now() 