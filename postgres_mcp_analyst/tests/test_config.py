from pathlib import Path

import pytest
from postgres_mcp.config import DatabaseConfig, load_environment


def test_loads_dotenv_values_without_overriding_process_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read dotenv settings while preserving existing environment values."""
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "PGHOST=dotenv-host\n"
        "PGPORT=5433\n"
        "PGDATABASE=analytics\n"
        "PGUSER=reader\n"
        "PGPASSWORD=dotenv-secret\n",
        encoding="utf-8",
    )
    for key in ("PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("PGHOST", "environment-host")

    load_environment(dotenv_path)
    config = DatabaseConfig.from_environment()

    assert config.host == "environment-host"
    assert config.port == 5433
    assert config.database == "analytics"
    assert config.username == "reader"
    assert config.password == "dotenv-secret"
