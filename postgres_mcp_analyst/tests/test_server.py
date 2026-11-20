import json
import subprocess
import sys


def test_module_entry_point_responds_to_mcp_initialize() -> None:
    """Verify launching the module starts the MCP stdio server."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "pytest", "version": "1.0"},
        },
    }

    result = subprocess.run(
        [sys.executable, "-m", "postgres_mcp.server"],
        input=f"{json.dumps(request)}\n",
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    responses = [
        json.loads(line)
        for line in result.stdout.splitlines()
        if line.strip()
    ]
    assert len(responses) == 1
    assert responses[0]["id"] == 1
    server_name = responses[0]["result"]["serverInfo"]["name"]
    assert server_name == "postgres-mcp-analyst"
