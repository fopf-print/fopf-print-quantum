from quantum import settings

from ._pg_connector_impl import Postgres

db = Postgres(settings.POSTGRES_CONNECTION_URI)

__all__ = ['db', 'Postgres']
