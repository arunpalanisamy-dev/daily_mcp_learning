# PostgreSQL MCP Analyst

This project provides a local Model Context Protocol (MCP) server that lets
Claude inspect a PostgreSQL database and answer questions using read-only SQL.
The server communicates with Claude over standard input/output (stdio); it does
not expose a network port.

## Requirements

- Windows
- Python 3.13 or newer
- [`uv`](https://docs.astral.sh/uv/) installed and available in PowerShell
- PostgreSQL reachable from this computer
- Claude Desktop (or another MCP client that supports stdio servers)

## Step 1: Create a PostgreSQL read-only user

Use an administrator account to create a dedicated account for the MCP server.
Grant it access only to the database, schemas, and tables Claude is allowed to
read. Do not use a PostgreSQL administrator account for the MCP connection.

For example, run the following SQL, replacing the database name and password:

```sql
CREATE ROLE mcp_reader WITH LOGIN PASSWORD 'replace-with-a-strong-password';
GRANT CONNECT ON DATABASE your_database TO mcp_reader;
GRANT USAGE ON SCHEMA public TO mcp_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_reader;
```

To grant access to tables created in the future, run this as the owner of those
tables (or specify the owner with `FOR ROLE`):

```sql
ALTER DEFAULT PRIVILEGES FOR ROLE table_owner IN SCHEMA public
  GRANT SELECT ON TABLES TO mcp_reader;
```

Repeat the schema grants for each schema Claude should access. The default
privileges command applies only to future objects created by the specified
owner; it does not grant access to existing tables.

## Step 2: Install the project

Open PowerShell and change to the project directory:

```powershell
Set-Location 'D:\ncv_labs\research_projects\mcp_learning\postgres_mcp_analyst'
```

Install the project and its dependencies:

```powershell
uv sync
```

This creates the project's `.venv` environment and installs the
`postgres-mcp-analyst` command. Run this step again whenever project
dependencies change.

## Step 3: Add your PostgreSQL connection settings

Create a file named `.env` in the project directory. For example, open it in
Notepad:

```powershell
notepad .env
```

Add your connection settings, replacing the example values:

```dotenv
PGHOST=localhost
PGPORT=5432
PGDATABASE=your_database
PGUSER=mcp_reader
PGPASSWORD=replace-with-your-postgres-password
PGSSLMODE=prefer
```

`PGHOST`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD` are required. `PGPORT`
defaults to `5432`; `PGSSLMODE` is optional. Use the SSL mode required by your
PostgreSQL host, such as `require` for a hosted database that requires TLS.

The server loads `.env` from the project directory. Environment variables
provided by Windows or the MCP client take precedence over values in `.env`.
The `.env` file is Git-ignored: keep your real credentials in it and never
commit or share it.

## Step 4: Check the database connection

From the project directory, run:

```powershell
uv run python -c "from postgres_mcp.database import get_connection; connection = get_connection(); connection.close(); print('PostgreSQL connection successful')"
```

If the command fails, check the host, port, database name, username, password,
SSL mode, network access, and PostgreSQL grants before setting up Claude.

## Step 5: Add the server to Claude Desktop

Open Claude Desktop's MCP configuration file:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

If the file already contains other MCP servers, add the `postgres_mcp` entry
inside its existing `mcpServers` object. Do not replace the rest of the file.
Use the following configuration:

```json
{
  "mcpServers": {
    "postgres_mcp": {
      "command": "D:\\ncv_labs\\research_projects\\mcp_learning\\postgres_mcp_analyst\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "postgres_mcp.server"
      ],
      "env": {}
    }
  }
}
```

The `command` path must point to the Python executable created by `uv sync`.
The `-m postgres_mcp.server` arguments start the MCP server module; do not
configure the Python executable by itself. If the project is in a different
directory, update the path accordingly.

You can optionally put `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`,
and `PGSSLMODE` in the JSON `"env"` object instead of `.env`. Avoid storing
credentials in configuration files that may be shared or committed.

## Step 6: Restart Claude and verify the tools

Save the configuration, fully quit Claude Desktop, and start it again. Confirm
that these PostgreSQL tools are available:

1. `list_database_tables` — lists tables and views visible to the database user.
2. `describe_database_table` — shows a table's columns and data types.
3. `run_query` — runs a read-only `SELECT` query.

Try asking Claude to list the available tables. Then ask it to describe a table
and answer a question about a small number of rows.

Example request for the query tool:

```sql
SELECT id, created_at
FROM public.your_table
ORDER BY created_at DESC
LIMIT 20;
```

The query tool returns up to 100 rows by default. It accepts a `max_rows`
between 1 and 500 to request a different limit.

## Security and query behavior

- Every database operation runs in a read-only transaction.
- Each statement has a 15-second timeout.
- Only one `SELECT` statement is allowed. Write statements, locking clauses,
  and known side-effecting functions are rejected.
- Use a PostgreSQL account with the least privileges needed. Read-only SQL
  validation is an extra safeguard, not a substitute for database permissions.
- Never put real passwords in source code or commit them to Git.

## Troubleshooting

### Claude reports that the server disconnected during initialization

Check that the MCP entry's command points to the project's `.venv\Scripts\python.exe`
and its arguments are exactly `["-m", "postgres_mcp.server"]`. Then run
`uv sync` from the project directory and restart Claude Desktop. A missing
`-m postgres_mcp.server` argument can cause Python to exit without starting the
MCP stdio server.

### The server starts, but a database tool reports a connection error

Check that `.env` is in the project root (next to `pyproject.toml`) and that
the required `PG*` values are correct. Verify that PostgreSQL accepts
connections from this computer and that the configured user can connect to the
database.

### The server connects, but a table is missing or access is denied

Check that the database user has `USAGE` on the table's schema and `SELECT` on
the table. The user can only discover and query objects it is allowed to access.

### Check the local tests

From the project directory, run:

```powershell
uv run pytest -q
```
