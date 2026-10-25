"""PostgreSQL connection helpers (psycopg 3).

Connection settings come from the libpq environment variables
(PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD), loaded from the project .env.
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence

import psycopg
from psycopg.rows import dict_row

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def load_env(path: Path = ENV_PATH) -> None:
    """Read KEY=VALUE lines into os.environ without overriding values already set."""
    path = Path(path)
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()


def _connect() -> psycopg.Connection:
    # libpq reads the PG* environment variables.
    return psycopg.connect(row_factory=dict_row, connect_timeout=5)


@contextmanager
def connection() -> Iterator[psycopg.Connection]:
    """Yield a connection in a transaction: commit on success, roll back on error."""
    with _connect() as conn:
        yield conn


def fetch_all(sql: str, params: Optional[Sequence[Any]] = None) -> list[dict]:
    with connection() as conn:
        return conn.execute(sql, params).fetchall()


def fetch_one(sql: str, params: Optional[Sequence[Any]] = None) -> Optional[dict]:
    with connection() as conn:
        return conn.execute(sql, params).fetchone()
