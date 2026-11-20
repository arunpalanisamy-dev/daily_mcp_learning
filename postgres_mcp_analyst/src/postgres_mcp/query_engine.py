"""Read-only SQL query execution."""

import json
from typing import Any

from postgres_mcp.database import readonly_connection
from postgres_mcp.security import validate_readonly_query

DEFAULT_MAX_ROWS = 100
MAX_ALLOWED_ROWS = 500


def execute_query(sql: str, max_rows: int = DEFAULT_MAX_ROWS) -> str:
    """Run a single read-only SELECT and return a bounded JSON result."""
    if not 1 <= max_rows <= MAX_ALLOWED_ROWS:
        raise ValueError(f"max_rows must be between 1 and {MAX_ALLOWED_ROWS}")
    validate_readonly_query(sql)

    with readonly_connection() as connection, connection.cursor(
        name="postgres_mcp_query"
    ) as cursor:
        cursor.execute(sql)
        columns = [column.name for column in cursor.description or ()]
        fetched_rows = cursor.fetchmany(max_rows + 1)

    truncated = len(fetched_rows) > max_rows
    rows: list[dict[str, Any]] = fetched_rows[:max_rows]
    return json.dumps(
        {
            "columns": columns,
            "rows": rows,
            "returned_rows": len(rows),
            "truncated": truncated,
            "max_rows": max_rows,
        },
        default=str,
    )
