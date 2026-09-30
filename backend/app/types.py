from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


def utcnow() -> datetime:
    return datetime.now(UTC)


class UTCDateTime(TypeDecorator):
    """Horodatage toujours stocké et relu en UTC avec fuseau explicite.

    PostgreSQL stocke un `timestamptz` ; SQLite (tests) n'a pas de fuseau, on
    le réattache donc à la lecture pour que l'API renvoie toujours `...Z`/`+00:00`.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value
