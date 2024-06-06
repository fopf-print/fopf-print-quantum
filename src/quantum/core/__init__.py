from quantum import settings

from ._pg_connector_impl import Postgres

db = Postgres(settings.postgres_connection_uri)

__all__ = ['db', 'Postgres']
