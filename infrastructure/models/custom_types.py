from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import DateTime, String, TypeDecorator

class UUIDType(TypeDecorator):
    """Platform-independent UUID type."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value: Optional[UUID], dialect: Any) -> Optional[str]:
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value: Optional[str], dialect: Any) -> Optional[UUID]:
        if value is None:
            return None
        return UUID(value)

class DateTimeType(TypeDecorator):
    """Platform-independent DateTime type."""
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: Optional[datetime], dialect: Any) -> Optional[datetime]:
        if value is None:
            return None
        return value.replace(microsecond=0)

    def process_result_value(self, value: Optional[datetime], dialect: Any) -> Optional[datetime]:
        if value is None:
            return None
        return value.replace(microsecond=0)