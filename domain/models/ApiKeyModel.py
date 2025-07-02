from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional
import json

from domain.models.Base import Base
from domain.models.UserModel import UserModel
from domain.entities.api_key import ApiKey

class ApiKeyModel(Base):
    """
    SQLAlchemy ORM model for ApiKey entity.

    This model represents the database structure for API keys and handles the persistence
    of ApiKey entities. It should not contain domain logic, only persistence-related code.
    """
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)
    key_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID for the key
    key_value = Column(String(64), unique=True, nullable=False, index=True)  # The actual API key value
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # A name for the API key (e.g., "Mobile App")
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_used_at = Column(DateTime, nullable=True)

    scopes = Column(JSON, nullable=True, default=lambda: json.dumps([]))
    allowed_ips = Column(JSON, nullable=True, default=lambda: json.dumps([]))
    allowed_user_agents = Column(JSON, nullable=True, default=lambda: json.dumps([]))

    # Relationships
    user = relationship('UserModel', backref='api_keys')

    def to_domain(self) -> ApiKey:
        """
        Converts the ApiKeyModel instance to a domain ApiKey entity.
        """
        return ApiKey(
            key_id=self.key_id,
            key_value=self.key_value,
            user_id=self.user_id,
            name=self.name,
            expires_at=self.expires_at,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_used_at=self.last_used_at,
            scopes=json.loads(self.scopes) if self.scopes else [],
            allowed_ips=json.loads(self.allowed_ips) if self.allowed_ips else [],
            allowed_user_agents=json.loads(self.allowed_user_agents) if self.allowed_user_agents else []
        )

    def __repr__(self):
        return f"<ApiKeyModel(id={self.id}, key_id={self.key_id}, name={self.name}, user_id={self.user_id})>"
