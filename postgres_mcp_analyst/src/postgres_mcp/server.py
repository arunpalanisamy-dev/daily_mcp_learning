"""PostgreSQL MCP server exposing safe, read-only database tools."""

import asyncio
import logging

from mcp.server.mcpserver import MCPServer

from postgres_mcp.query_engine import execute_query
from postgres_mcp.schema_inspector import describe_table, list_tables

logger = logging.getLogger(__name__)

server = MCPServer(
    name="postgres-mcp-analyst",
    version="0.1.0",
    instructions=(
        "Use list_database_tables and describe_database_table to discover "
        "the database schema. Use run_query to answer questions with "
        "read-only SELECT statements."
    ),
)


@server.tool()
def list_database_tables(schema: str | None = None) -> str:
    """List visible database tables and views.

    Args:
        schema: Optional schema name to filter the results.

    Returns:
        A JSON string containing the matching tables and views.
    """
    return list_tables(schema)


@server.tool()
def describe_database_table(table_name: str, schema: str | None = None) -> str:
    """Describe the columns of a database table or view.

    Args:
        table_name: Name of the table or view to describe.
        schema: Optional schema name to disambiguate the table.

    Returns:
        A JSON string containing the table's column metadata.
    """
    return describe_table(table_name, schema)


@server.tool()
def run_query(sql: str, max_rows: int = 100) -> str:
    """Run one read-only PostgreSQL SELECT query.

    Args:
        sql: A single PostgreSQL SELECT statement.
        max_rows: Maximum number of result rows to return.

    Returns:
        A JSON string containing the query columns and bounded result rows.
    """
    return execute_query(sql, max_rows)


def main() -> None:
    """Start the MCP server over stdio for desktop MCP clients."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting PostgreSQL MCP server over stdio")
    asyncio.run(server.run_stdio_async())


if __name__ == "__main__":
    main()
