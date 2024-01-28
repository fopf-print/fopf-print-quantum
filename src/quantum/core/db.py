import sqlite3
from typing import Any, Iterable

from quantum import settings

_db = None


def _get_db():
    global _db
    if _db is not None:
        return _db

    _db = sqlite3.connect(f'{settings.SQLITE_DB_PATH_PREFIX}/quantum.db')

    with open(f'{settings.SQLITE_DB_PATH_PREFIX}/init_quantum.sql') as f:
        init_scripts = f.read()

    _db.executescript(init_scripts)
    _db.commit()
    return _db


async def execute(sql: str, parameters: Iterable[Any] = ()):
    db = _get_db()

    db.execute(sql, parameters)
    db.commit()


async def fetchall(sql: str, parameters: Iterable[Any]) -> list[dict[str, Any]]:
    db = _get_db()

    # типы заедут, когда переедет что-то нормальное
    cursor = db.cursor()
    cursor.execute(sql, parameters)

    keys = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    return [
        {
            k: v for k, v in zip(keys, row)
        }
        for row in rows
    ]
