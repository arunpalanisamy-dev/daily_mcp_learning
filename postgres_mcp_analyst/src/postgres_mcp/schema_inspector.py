"""Read-only PostgreSQL schema inspection helpers."""

import json
from typing import Any

from postgres_mcp.database import readonly_connection


def list_tables(schema: str | None = None) -> str:
    """Return user-visible tables and views, optionally filtered by schema."""
    query = """
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
          AND table_type IN ('BASE TABLE', 'VIEW')
    """
    params: tuple[str, ...] = ()
    if schema is not None:
        query += " AND table_schema = %s"
        params = (schema,)
    query += " ORDER BY table_schema, table_name"

    with readonly_connection() as connection, connection.cursor() as cursor:
        cursor.execute(query, params)
        tables: list[dict[str, Any]] = cursor.fetchall()
    return json.dumps({"tables": tables}, default=str)


def describe_table(table_name: str, schema: str | None = None) -> str:
    """Return column metadata for a table or view visible to the user."""
    query = """
        SELECT table_schema, table_name, column_name, data_type,
               is_nullable, column_default, ordinal_position
        FROM information_schema.columns
        WHERE table_name = %s
    """
    params: tuple[str, ...] = (table_name,)
    if schema is not None:
        query += " AND table_schema = %s"
        params = (table_name, schema)
    query += " ORDER BY table_schema, ordinal_position"

    with readonly_connection() as connection, connection.cursor() as cursor:
        cursor.execute(query, params)
        columns: list[dict[str, Any]] = cursor.fetchall()
    return json.dumps({"columns": columns}, default=str)
