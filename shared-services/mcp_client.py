import json
import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger("MCPClient")

class MCPContext7Client:
    """
    A reusable client wrapper for connecting to the Context7 MCP server using the 
    official Model Context Protocol (MCP) HTTP transport over Server-Sent Events (SSE).
    It dynamically loads the launch URL and headers from the local IDE MCP config.
    """
    def __init__(self):
        self.config_path = os.path.expanduser("~/.gemini/config/mcp_config.json")

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[ClientSession, None]:
        """
        Establishes an SSE connection, initializes the session, and yields the session
        for calling tools or interacting with the MCP server.
        """
        if not os.path.exists(self.config_path):
            raise ValueError(f"MCP Config not found at {self.config_path}")

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse MCP Config: {e}")

        c7_config = config_data.get("mcpServers", {}).get("context7")
        if not c7_config:
            raise ValueError("Context7 MCP server configuration not found in mcp_config.json")

        server_url = c7_config.get("serverUrl")
        headers = c7_config.get("headers", {})

        if not server_url:
            raise ValueError("Context7 serverUrl not found in mcp_config.json")

        # Inject our API key from the local `.env` if it overrides it
        local_key = os.getenv("CONTEXT7_API_KEY")
        if local_key:
            headers["CONTEXT7_API_KEY"] = local_key

        try:
            # Connect to the SSE endpoint using the config URL
            async with sse_client(server_url, headers=headers) as (read_stream, write_stream):
                # Initialize the MCP Session over the established streams
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    yield session
        except Exception as e:
            logger.error(f"Failed to establish Context7 MCP SSE session: {e}")
            raise
