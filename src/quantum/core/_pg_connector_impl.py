from contextlib import asynccontextmanager
from typing import Any, Iterable

import asyncpg


class Postgres:
    __slots__ = ['_uri']

    def __init__(self, uri: str):
        self._uri = uri

    @asynccontextmanager
    async def _ensure_connected(self):
        con = await asyncpg.connect(self._uri)
        try:
            yield con
        finally:
            await con.close()

    async def execute(self, sql: str, parameters: Iterable[Any] = ()):
        async with self._ensure_connected() as con:
            await con.execute(sql, *parameters)  # type: ignore[attr-defined]

    async def fetchall(self, sql: str, parameters: Iterable[Any] = ()) -> list[dict[str, Any]]:
        async with self._ensure_connected() as con:
            rows = await con.fetch(sql, *parameters)  # type: ignore[attr-defined]
        return [dict(r) for r in rows]

    @asynccontextmanager
    async def transaction(self):
        async with self._ensure_connected() as con:
            yield con.transaction()    # type: ignore[attr-defined]
