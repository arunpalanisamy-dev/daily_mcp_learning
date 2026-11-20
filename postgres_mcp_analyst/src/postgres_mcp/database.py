"""PostgreSQL connections and read-only transaction helpers."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg.rows import dict_row

from postgres_mcp.config import DatabaseConfig

logger = logging.getLogger(__name__)

STATEMENT_TIMEOUT = "15000ms"


def get_connection() -> psycopg.Connection[Any]:
    """Open a PostgreSQL connection using the configured environment."""
    config = DatabaseConfig.from_environment()
    try:
        connection = psycopg.connect(
            **config.connection_kwargs(),
            row_factory=dict_row,
        )
    except psycopg.OperationalError:
        logger.exception("Could not connect to PostgreSQL")
        raise

    logger.info("PostgreSQL connection established")
    return connection


@contextmanager
def readonly_connection() -> Iterator[psycopg.Connection[Any]]:
    """Yield a connection in a read-only transaction with a query timeout."""
    connection = get_connection()
    try:
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute(
                    "SELECT set_config('statement_timeout', %s, true)",
                    (STATEMENT_TIMEOUT,),
                )
            yield connection
    finally:
        connection.close()
