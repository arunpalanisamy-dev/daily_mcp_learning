"""PostgreSQL connection configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_SSL_MODES = {
    "disable",
    "allow",
    "prefer",
    "require",
    "verify-ca",
    "verify-full",
}
DOTENV_PATH = Path(__file__).resolve().parents[2] / ".env"


def load_environment(
    dotenv_path: Path = DOTENV_PATH,
) -> None:
    """Load project settings without overriding environment variables."""
    load_dotenv(dotenv_path=dotenv_path, override=False)


load_environment()


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    database: str
    username: str
    password: str
    sslmode: str | None = None

    @classmethod
    def from_environment(cls) -> "DatabaseConfig":
        """Create config from PostgreSQL environment variables."""
        required = ("PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD")
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            missing_names = ", ".join(missing)
            raise ValueError(
                f"Missing database configuration: {missing_names}"
            )

        try:
            port = int(os.getenv("PGPORT", "5432"))
        except ValueError as exc:
            raise ValueError("PGPORT must be a valid integer") from exc
        if not 1 <= port <= 65535:
            raise ValueError("PGPORT must be between 1 and 65535")

        sslmode = os.getenv("PGSSLMODE")
        if sslmode and sslmode not in _SSL_MODES:
            choices = ", ".join(sorted(_SSL_MODES))
            raise ValueError(
                f"PGSSLMODE must be one of: "
                f"{choices}"
            )

        return cls(
            host=os.environ["PGHOST"],
            port=port,
            database=os.environ["PGDATABASE"],
            username=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
            sslmode=sslmode,
        )

    def connection_kwargs(self) -> dict[str, Any]:
        """Return keyword arguments accepted by psycopg.connect."""
        kwargs: dict[str, Any] = {
            "host": self.host,
            "port": self.port,
            "dbname": self.database,
            "user": self.username,
            "password": self.password,
            "connect_timeout": 5,
            "application_name": "postgres_mcp_analyst",
        }
        if self.sslmode:
            kwargs["sslmode"] = self.sslmode
        return kwargs
