from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from domain.models.Base import Base
from domain.entities.user import User

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class UserModel(Base):
    """
    SQLAlchemy ORM model for User entity.

    This model represents the database structure for users and handles the persistence
    of User entities. It should not contain domain logic, only persistence-related code.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 can be up to 45 chars
    verification_token = Column(String(128), nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    password_reset_token = Column(String(128), nullable=True)
    password_reset_token_expires_at = Column(DateTime, nullable=True)

    # Relationships
    roles = relationship('RoleModel', secondary=user_roles, backref='users')

    def to_domain(self) -> User:
        """
        Converts the UserModel instance to a domain User entity.
        """
        user = User(
            id=self.id,
            username=self.username,
            email=self.email,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_login_at=self.last_login_at,
            first_name=self.first_name,
            last_name=self.last_name,
            is_verified=self.is_verified,
            last_login_ip=self.last_login_ip,
            verification_token=self.verification_token,
            verification_token_expires_at=self.verification_token_expires_at,
            password_reset_token=self.password_reset_token,
            password_reset_token_expires_at=self.password_reset_token_expires_at
        )

        # Set password hash directly to avoid hashing again
        user._password_hash = self.password_hash

        # Add roles as Role objects
        for role_model in self.roles:
            user._roles.append(role_model.to_domain())

        # Add API keys as ApiKey objects
        if hasattr(self, 'api_keys'):
            for api_key_model in self.api_keys:
                user._api_keys.append(api_key_model.to_domain())

        # Add refresh tokens as RefreshToken objects
        if hasattr(self, 'refresh_tokens'):
            for refresh_token_model in self.refresh_tokens:
                user._refresh_tokens.append(refresh_token_model.to_domain())

        return user
