# Run the Simple MCP Server

## Test with MCP Inspector

1. Install Python 3.12 or later and [uv](https://docs.astral.sh/uv/).
2. From this project folder, install dependencies:

   ```powershell
   uv sync
   ```

3. Start the server with the MCP Inspector:

   ```powershell
   uv run mcp dev server.py
   ```

   Open the Inspector URL shown in the terminal to connect and try the tools.

## Connect to Claude Desktop

Claude Desktop starts the server using its `stdio` transport. Add or update the
server entry in:

```text
C:\Users\NCV_C\AppData\Roaming\Claude\claude_desktop_config.json
```

Merge this entry under the existing `mcpServers` object; keep the other
settings in the file:

```json
{
  "mcpServers": {
    "my-first-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "D:\\ncv_labs\\research_projects\\mcp_learning\\simple_mcp_server",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

The current config already has a `my-first-mcp` entry. Replace that entry if
you want to use the `uv` command above; do not replace the whole config file.
If Claude Desktop cannot find `uv`, use the full path to `uv.exe` as
`command`. Restart Claude Desktop after changing the config, then call the
server's tools in a chat. Tool results appear in the chat.
