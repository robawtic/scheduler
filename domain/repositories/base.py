from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository interface with common CRUD operations."""

    @abstractmethod
    def save(self, entity: T) -> None:
        """Save or update an entity."""
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[T]:
        """Retrieve an entity by its UUID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all entities."""
        pass

    @abstractmethod
    def delete(self, id: UUID) -> None:
        """Delete an entity."""
        pass 