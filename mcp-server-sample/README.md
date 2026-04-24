# MCP server sample

A minimal Model Context Protocol server written in Python. Exposes 2 resources and 1 tool.

## What it shows

- How to define **resources** (content the client can load into context on demand)
- How to define a **tool** (executable function the model can call)
- How to run an MCP server over stdio (the default transport)

## Prerequisites

- Python 3.11+

## Run it

```bash
cd mcp-server-sample
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python server.py
```

The server listens on stdio. To actually exercise it, point an MCP client at this process.

## Connect from Claude Desktop

Edit your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add:

```json
{
  "mcpServers": {
    "field-notes-sample": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-server-sample/server.py"]
    }
  }
}
```

Restart Claude Desktop. You should see the server listed in the MCP indicator, and you can ask things like:

- "What's the status of order ORD-1002?" (triggers the tool)
- "What are the company shipping policies?" (loads the policies resource)

## Connect from a Strands agent

See the sibling [`strands-hello-world/`](../strands-hello-world) module. Strands ships an MCP client you can register against this server to let the agent pull resources or invoke tools.

## Design notes

**Resources vs. tools — when to use which:**

| Pattern | Use a **resource** | Use a **tool** |
|---------|--------------------|-----------------|
| Read-only reference data | ✓ | |
| Action with side effects | | ✓ |
| Returns a value the model should reason about | | ✓ |
| Large document the model may or may not need | ✓ | |
| Parameterized query | | ✓ |

**Why this matters:** resources are loaded by the client into context; tools are invoked by the model at runtime. Mixing them up leads to agents that either flood context with unused data or miss data they needed because it was not exposed as a tool.

> See Week 4 of Field Notes on **why connecting too many MCP servers degrades agent performance** — [article](https://awstip.com/i-connected-five-mcp-servers-to-my-ide-my-ai-agent-got-dumber-92c2e658f487).

## References

- [Model Context Protocol specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
