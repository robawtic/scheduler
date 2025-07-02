from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

# Define naming conventions for automatic constraint/index names
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming conventions
metadata = MetaData(naming_convention=NAMING_CONVENTION)

# Create declarative base
Base = declarative_base(metadata=metadata) 