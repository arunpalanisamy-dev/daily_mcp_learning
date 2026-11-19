
import sys
from datetime import datetime
from io import TextIOWrapper

import anyio
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

async def _nonblank_stdin():
    stdin = anyio.wrap_file(TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace"))
    async for line in stdin:
        if line.strip():
            yield line

class _BlankLineTolerantFastMCP(FastMCP):
    async def run_stdio_async(self) -> None:
        async with stdio_server(stdin=_nonblank_stdin()) as (read_stream, write_stream):
            await self._mcp_server.run(
                read_stream,
                write_stream,
                self._mcp_server.create_initialization_options(),
            )

# Create MCP server
mcp = _BlankLineTolerantFastMCP("My First MCP Server")

# Tool 1: Get current date and time
@mcp.tool()
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().astimezone().isoformat()

# Tool 2: Add two numbers
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b

# Tool 3: Personalized greeting
@mcp.tool()
def get_greeting(name: str) -> str:
    """Generate a personalized greeting."""
    return f"Hello {name}! Welcome to MCP."

if __name__ == "__main__":
    mcp.run()
