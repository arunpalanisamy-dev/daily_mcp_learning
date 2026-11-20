"""Validation for SQL statements accepted by the query tool."""

from sqlglot import ParseError, exp, parse

_FORBIDDEN_EXPRESSIONS = {
    "command",
    "delete",
    "insert",
    "into",
    "lock",
    "merge",
    "update",
}
_FORBIDDEN_FUNCTIONS = {
    "PG_ADVISORY_LOCK",
    "PG_ADVISORY_XACT_LOCK",
    "PG_CANCEL_BACKEND",
    "PG_NOTIFY",
    "PG_SLEEP",
    "PG_TERMINATE_BACKEND",
    "SET_CONFIG",
}

def validate_readonly_query(sql: str) -> None:
    """Allow one SELECT statement and reject write or locking operations."""
    if not sql.strip():
        raise ValueError("SQL query must not be empty")

    try:
        statements = parse(sql, read="postgres")
    except ParseError as exc:
        raise ValueError(f"Invalid PostgreSQL query: {exc}") from exc

    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise ValueError("Only one SELECT query is allowed")

    statement = statements[0]
    for node in statement.walk():
        if node.key.lower() in _FORBIDDEN_EXPRESSIONS:
            raise ValueError("Write and locking operations are not allowed")
        if isinstance(node, exp.Func):
            if isinstance(node, exp.Anonymous):
                function_name = node.name
            else:
                function_name = node.sql_name()
            if function_name.upper() in _FORBIDDEN_FUNCTIONS:
                raise ValueError(
                    f"The {function_name} function is not allowed"
                )
