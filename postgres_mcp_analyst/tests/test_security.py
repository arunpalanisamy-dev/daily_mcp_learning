import pytest

from postgres_mcp.query_engine import execute_query
from postgres_mcp.security import validate_readonly_query


def test_accepts_select_and_read_only_cte() -> None:
    """Allow plain SELECT queries and read-only common table expressions."""
    validate_readonly_query("SELECT id FROM customers;")
    validate_readonly_query(
        "WITH active AS (SELECT id FROM customers) SELECT id FROM active"
    )


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM customers",
        "SELECT id FROM customers; SELECT id FROM orders",
        "SELECT id INTO copied_customers FROM customers",
        "SELECT id FROM customers FOR UPDATE",
        (
            "WITH removed AS (DELETE FROM customers RETURNING id) "
            "SELECT id FROM removed"
        ),
    ],
)
def test_rejects_non_select_and_multiple_statements(sql: str) -> None:
    """Reject writes, locks, and multiple SQL statements."""
    with pytest.raises(ValueError):
        validate_readonly_query(sql)


@pytest.mark.parametrize("sql", ["", "  ", "SELECT pg_sleep(1)"])
def test_rejects_empty_and_side_effecting_queries(sql: str) -> None:
    """Reject empty statements and known side-effecting functions."""
    with pytest.raises(ValueError):
        validate_readonly_query(sql)


@pytest.mark.parametrize("max_rows", [0, 501])
def test_query_row_limit_is_bounded_before_connecting(max_rows: int) -> None:
    """Reject row limits outside the supported range before database access."""
    with pytest.raises(ValueError):
        execute_query("SELECT 1", max_rows)
