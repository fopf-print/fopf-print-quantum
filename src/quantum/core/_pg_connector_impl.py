from typing import Any, Iterable

import asyncpg


class Postgres:
    def __init__(self, uri: str):
        self._db = None
        self._uri = uri

    async def _ensure_connected(self):
        if self._db is None:
            self._db = await asyncpg.connect(self._uri)

    async def execute(self, sql: str, parameters: Iterable[Any] = ()):
        await self._ensure_connected()            # вот тут проверяем, что оно не None
        await self._db.execute(sql, *parameters)  # type: ignore[attr-defined]

    async def fetchall(self, sql: str, parameters: Iterable[Any] = ()) -> list[dict[str, Any]]:
        await self._ensure_connected()                 # вот тут проверяем, что оно не None
        rows = await self._db.fetch(sql, *parameters)  # type: ignore[attr-defined]
        return [dict(r) for r in rows]

    async def transaction(self):
        raise RuntimeError('unimplemented :(')
