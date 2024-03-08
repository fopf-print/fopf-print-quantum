from ._pg_connector_impl import Postgres
from quantum import settings

db = Postgres(settings.POSTGRES_CONNECTION_URI)

__all__ = ['db', 'Postgres']
