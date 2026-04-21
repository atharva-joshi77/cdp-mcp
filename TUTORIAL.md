# CDP MCP Server — Command Tutorial

A step-by-step guide to installing, configuring, and running the **cdp-mcp-server** — an MCP (Model Context Protocol) server for Acquia Customer Data Platform (CDP).

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Running the Server](#4-running-the-server)
5. [Connecting to an MCP Client](#5-connecting-to-an-mcp-client)
6. [Authentication Modes](#6-authentication-modes)
7. [Available Tools Reference](#7-available-tools-reference)
8. [Available Resources](#8-available-resources)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

| Requirement | Minimum Version |
|-------------|-----------------|
| Python      | 3.11+           |
| pip         | 23.0+           |
| Git         | any             |

Verify your Python version:

```bash
python3 --version   # Must be >= 3.11
```

You will also need valid credentials for the Acquia CDP API (OAuth2 client credentials **or** a pre-existing bearer token).

---

## 2. Installation

### 2a. Clone the repository

```bash
git clone <your-repo-url> cdp-mcp
cd cdp-mcp
```

### 2b. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 2c. Install the package

**Editable install (development):**

```bash
pip install -e .
```

This installs the `cdp-mcp` CLI command and all dependencies:

| Package            | Purpose                           |
|--------------------|-----------------------------------|
| `mcp>=1.13.0`      | MCP protocol framework (FastMCP)  |
| `httpx>=0.27.0`    | Async HTTP client for CDP API     |
| `pydantic>=2.0.0`  | Data validation & models          |
| `pydantic-settings>=2.0.0` | Env-based config loading |
| `python-dotenv>=1.0.0` | `.env` file support           |

**Standard install (production):**

```bash
pip install .
```

### 2d. Verify the installation

```bash
# Confirm the command is on your PATH
which cdp-mcp
# Expected: /path/to/cdp-mcp/.venv/bin/cdp-mcp
```

> **Note:** `cdp-mcp` does **not** support `--help`. Running it bare starts the stdio server immediately and waits for JSON-RPC input (it will appear to "hang"). This is normal — the server is designed to be driven by an MCP client, not used interactively.

---

## 3. Configuration

The server loads configuration from **environment variables** and/or a **`.env` file** in the working directory.

### 3a. Create a `.env` file

Copy the example and fill in your credentials:

```bash
cp .env.example .env
```

### 3b. Edit `.env`

```env
# ── Environment Selector ─────────────────────────────────
# Options: dev, qa, prod
CDP_ENVIRONMENT=dev

# ── Base URLs (override only if using non-standard endpoints) ──
CDP_BASE_URL_DEV=https://dev-api6.agilone.com
CDP_BASE_URL_QA=https://qa-api6.agilone.com
CDP_BASE_URL_PROD=https://api.agilone.com

# ── Default Tenant ────────────────────────────────────────
# Optional. If set, tools use this tenant when no tenant_id is supplied.
CDP_TENANT_ID=12345

# ── OAuth2 Credentials (Option A — recommended) ──────────
CDP_CLIENT_ID=your-client-id
CDP_CLIENT_SECRET=your-client-secret
CDP_USERNAME=your-username
CDP_PASSWORD=your-password

# ── Static Bearer Token (Option B — alternative) ─────────
# If set, OAuth2 is skipped entirely.
# CDP_AUTH_TOKEN=eyJhbGciOiJSUzI1NiIs...
```

> **Important:** You must provide either **OAuth2 credentials** (Option A) or a **static bearer token** (Option B). If `CDP_AUTH_TOKEN` is set, OAuth2 credentials are ignored.

### 3c. Environment variables (alternative to `.env`)

You can also export variables directly in your shell:

```bash
export CDP_ENVIRONMENT=dev
export CDP_TENANT_ID=12345
export CDP_CLIENT_ID=your-client-id
export CDP_CLIENT_SECRET=your-client-secret
export CDP_USERNAME=your-username
export CDP_PASSWORD=your-password
```

Environment variables take precedence over `.env` file values.

---

## 4. Running the Server

### 4a. Using the CLI entry point

```bash
cdp-mcp
```

### 4b. Using the Python module

```bash
python -m cdp_mcp
```

Both commands start the server on **stdio transport** — the server reads JSON-RPC messages from stdin and writes responses to stdout. This is the standard transport mode for MCP client integration.

> **Note:** The server does not produce human-readable output on its own. It is designed to be connected to an MCP-compatible client (see [Section 5](#5-connecting-to-an-mcp-client)).

### 4c. Quick smoke test

To verify the server starts without errors, you can pipe an `initialize` request:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | cdp-mcp
```

You should receive a JSON-RPC response containing the server's capabilities and tool list.

---

## 5. Connecting to an MCP Client

### 5a. Claude Desktop

Add the following to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cdp": {
      "command": "cdp-mcp",
      "env": {
        "CDP_ENVIRONMENT": "dev",
        "CDP_TENANT_ID": "12345",
        "CDP_CLIENT_ID": "your-client-id",
        "CDP_CLIENT_SECRET": "your-client-secret",
        "CDP_USERNAME": "your-username",
        "CDP_PASSWORD": "your-password"
      }
    }
  }
}
```

If you installed in a virtual environment, use the full path to the `cdp-mcp` binary:

```json
{
  "mcpServers": {
    "cdp": {
      "command": "/absolute/path/to/cdp-mcp/.venv/bin/cdp-mcp",
      "env": {
        "CDP_ENVIRONMENT": "dev",
        "CDP_TENANT_ID": "12345",
        "CDP_CLIENT_ID": "your-client-id",
        "CDP_CLIENT_SECRET": "your-client-secret",
        "CDP_USERNAME": "your-username",
        "CDP_PASSWORD": "your-password"
      }
    }
  }
}
```

### 5b. VS Code (GitHub Copilot / Copilot Chat)

Add to your VS Code `settings.json` or workspace `.vscode/mcp.json`:

```json
{
  "mcp": {
    "servers": {
      "cdp": {
        "command": "cdp-mcp",
        "env": {
          "CDP_ENVIRONMENT": "dev",
          "CDP_TENANT_ID": "12345",
          "CDP_CLIENT_ID": "your-client-id",
          "CDP_CLIENT_SECRET": "your-client-secret",
          "CDP_USERNAME": "your-username",
          "CDP_PASSWORD": "your-password"
        }
      }
    }
  }
}
```

### 5c. Using `uv` (without pre-installing)

If you use [uv](https://docs.astral.sh/uv/) as your Python package manager, you can run the server directly without installing:

```json
{
  "mcpServers": {
    "cdp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/cdp-mcp", "cdp-mcp"],
      "env": {
        "CDP_ENVIRONMENT": "dev",
        "CDP_TENANT_ID": "12345",
        "CDP_CLIENT_ID": "your-client-id",
        "CDP_CLIENT_SECRET": "your-client-secret",
        "CDP_USERNAME": "your-username",
        "CDP_PASSWORD": "your-password"
      }
    }
  }
}
```

### 5d. Local Ollama

Ollama does not natively act as an MCP client. You need a bridge that connects Ollama models to MCP servers. Below are three practical options:

#### Option 1: Open WebUI (recommended — full web UI)

[Open WebUI](https://github.com/open-webui/open-webui) is a self-hosted chat interface that supports both Ollama backends and MCP tool servers.

```bash
# 1. Make sure Ollama is running
ollama serve

# 2. Pull a model with tool-calling support
ollama pull gemma4
# or: ollama pull llama3.1, qwen2.5, mistral, etc.

# 3. Run Open WebUI via Docker
docker run -d \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

**Important:** Open WebUI's Tool Servers require an **HTTP endpoint**, but `cdp-mcp` runs on stdio. You must use a proxy to bridge stdio → HTTP.

**Step A — Install and run the Streamable HTTP proxy:**

```bash
# Install supergateway (stdio-to-HTTP bridge)
npm install -g supergateway

# Start the proxy (exposes cdp-mcp as a Streamable HTTP server on port 8006)
supergateway \
  --stdio "cdp-mcp" \
  --port 8006 \
  --outputTransport streamableHttp \
  --cors
```

Make sure your `.env` file (with CDP credentials) is in the directory where you run this command, or export the environment variables beforehand:

```bash
export CDP_ENVIRONMENT=dev
export CDP_TENANT_ID=12345
export CDP_CLIENT_ID=your-client-id
export CDP_CLIENT_SECRET=your-client-secret
export CDP_USERNAME=your-username
export CDP_PASSWORD=your-password

supergateway \
  --stdio "cdp-mcp" \
  --port 8006 \
  --outputTransport streamableHttp \
  --cors
```

> **Important:** The flag is `streamableHttp` (camelCase) — not `streamable-http`. The proxy will listen at `http://localhost:8006/mcp`.

**Step B — Configure Open WebUI:**

1. Open `http://localhost:3000` in your browser
2. Go to **Admin Panel → Settings → Tools → Manage Tool Servers**
3. Click **"+ Add Connection"** (the `+` button)
4. Set **Type** to **MCP Streamable HTTP**
5. Enter the URL:
   ```
   http://host.docker.internal:8006/mcp
   ```
   > Since Open WebUI runs inside Docker, you must use `host.docker.internal` (not `localhost`)
6. Click **Verify** — you should see a green checkmark confirming the connection
7. Click **Save**

**Step C — Use it:**

1. Select a tool-capable model (e.g., `gemma4`, `qwen3.5`, `llama3.1`)
2. In the chat input area, click the **"+"** button and enable the MCP tools under **Tool Servers**
3. Ask a question like: *"List all users for tenant 12345"*
4. The model will call the CDP MCP tools and return results

> **Tip:** If you get an error like "No tenant ID provided", make sure `CDP_TENANT_ID` is set in your `.env` file, or pass the tenant ID explicitly in your prompt (e.g., "List users for tenant 12345").

#### Option 2: mcphost (CLI — no UI)

[mcphost](https://github.com/mark3labs/mcphost) is a lightweight Go CLI that connects Ollama (or OpenAI-compatible) models directly to MCP servers.

```bash
# 1. Install mcphost
go install github.com/mark3labs/mcphost@latest
# or via Homebrew:
brew install mark3labs/tap/mcphost

# 2. Create an MCP config file
cat > ~/.mcp.json << 'EOF'
{
  "mcpServers": {
    "cdp": {
      "command": "/absolute/path/to/cdp-mcp/.venv/bin/cdp-mcp",
      "env": {
        "CDP_ENVIRONMENT": "dev",
        "CDP_TENANT_ID": "12345",
        "CDP_CLIENT_ID": "your-client-id",
        "CDP_CLIENT_SECRET": "your-client-secret",
        "CDP_USERNAME": "your-username",
        "CDP_PASSWORD": "your-password"
      }
    }
  }
}
EOF

# 3. Start an interactive chat session with Ollama
mcphost --config ~/.mcp.json --model ollama:gemma4
```

You get a REPL where the Ollama model can call CDP tools automatically.

#### Option 3: Continue.dev (VS Code extension)

[Continue](https://www.continue.dev/) is a VS Code extension that supports both Ollama as an LLM provider and MCP tool servers.

1. Install the **Continue** extension in VS Code
2. Configure Ollama as your model in `~/.continue/config.yaml`:

   ```yaml
   models:
     - name: gemma4
       provider: ollama
       model: gemma4
   ```

3. Add the CDP MCP server in `~/.continue/config.yaml`:

   ```yaml
   mcpServers:
     - name: cdp
       command: /absolute/path/to/cdp-mcp/.venv/bin/cdp-mcp
       env:
         CDP_ENVIRONMENT: dev
         CDP_TENANT_ID: "12345"
         CDP_CLIENT_ID: your-client-id
         CDP_CLIENT_SECRET: your-client-secret
         CDP_USERNAME: your-username
         CDP_PASSWORD: your-password
   ```

4. Open the Continue chat panel in VS Code — CDP tools are available to the Ollama model

> **Important:** For tool calling to work reliably, use an Ollama model that supports function/tool calling — e.g., `gemma4`, `llama3.1`, `qwen2.5`, `mistral`, or `command-r`. Smaller models or older architectures may not handle tools correctly.

### 5e. MCP Inspector (debugging)

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to interactively test the server:

```bash
# Install inspector globally
npx @modelcontextprotocol/inspector cdp-mcp
```

This opens a web UI where you can browse tools, send requests, and see responses.

---

## 6. Authentication Modes

The server supports two authentication strategies:

### Mode A: OAuth2 Password Grant (recommended)

Set all four credential variables:

```env
CDP_CLIENT_ID=your-client-id
CDP_CLIENT_SECRET=your-client-secret
CDP_USERNAME=your-username
CDP_PASSWORD=your-password
```

The server will automatically:
1. Request a token from `POST {baseUrl}/token?action=create`
2. Cache the token in memory
3. Refresh it 60 seconds before expiry
4. Inject `Authorization: Bearer <token>` into all API calls

### Mode B: Static Bearer Token

Set a pre-existing token directly:

```env
CDP_AUTH_TOKEN=eyJhbGciOiJSUzI1NiIs...
```

When `CDP_AUTH_TOKEN` is set, the OAuth2 flow is completely bypassed. The static token is sent as-is in all requests.

> **Warning:** Static tokens expire. You are responsible for rotating them manually.

---

## 7. Available Tools Reference

The server registers **~163 tools** across 8 domains. Every tool accepts an optional `tenant_id` parameter — if omitted, the default `CDP_TENANT_ID` from config is used.

### Permissions API (15 tools)

| Tool Name | Description |
|-----------|-------------|
| `cdp_list_users` | List all users for a tenant (paginated) |
| `cdp_get_user` | Get a user by ID |
| `cdp_create_user` | Create a new user |
| `cdp_update_user` | Update an existing user |
| `cdp_delete_user` | Delete a user |
| `cdp_list_roles` | List all roles |
| `cdp_get_role` | Get a role by ID |
| `cdp_create_role` | Create a new role |
| `cdp_update_role` | Update a role |
| `cdp_delete_role` | Delete a role |
| `cdp_list_clients` | List all API clients |
| `cdp_get_client` | Get a client by ID |
| `cdp_create_client` | Create a new API client |
| `cdp_update_client` | Update a client |
| `cdp_delete_client` | Delete a client |

### Data Warehouse API (21 tools)

| Tool Name | Description |
|-----------|-------------|
| `cdp_list_entities` | List data warehouse entity types |
| `cdp_get_entity` | Get entity type details |
| `cdp_create_entity` | Create a new entity type |
| `cdp_update_entity` | Update an entity type |
| `cdp_delete_entity` | Delete an entity type |
| `cdp_get_a360_profile` | Get A360 customer profile |
| `cdp_search_a360_profiles` | Search A360 profiles |
| `cdp_list_audiences` | List data warehouse audiences |
| `cdp_get_audience` | Get audience details |
| `cdp_create_audience` | Create an audience |
| `cdp_list_trackers` | List trackers |
| `cdp_get_tracker` | Get tracker details |
| `cdp_create_data_erasure` | Create a data erasure request |
| `cdp_get_data_erasure` | Get data erasure status |
| `cdp_list_offers` | List offers |
| `cdp_get_offer` | Get offer details |
| `cdp_create_offer` | Create an offer |
| `cdp_update_offer` | Update an offer |
| `cdp_delete_offer` | Delete an offer |
| `cdp_get_metadata` | Get data warehouse metadata |
| `cdp_list_dw_reports` | List data warehouse reports |

### Campaign API (24 tools)

Manage campaign definitions, audiences, dispatches, runs, actions, and templates.

Tool prefix: `cdp_*_campaign_*`, `cdp_*_dispatch_*`, `cdp_*_campaign_run_*`, `cdp_*_audience_def_*`, `cdp_*_campaign_template_*`

### Config API (30 tools)

Manage tenants, workflows, schedules, workflow jobs, UDMP tables, DQE rules, clusters, and summary customizations.

Tool prefix: `cdp_*_tenant_*`, `cdp_*_workflow_*`, `cdp_*_schedule_*`, `cdp_*_udmp_*`, `cdp_*_dqe_*`, `cdp_*_cluster_*`

### Connectors, Predictions & Alerts (27 tools)

Manage data connectors, connector templates, prediction models, and alert configurations.

Tool prefix: `cdp_*_connector_*`, `cdp_*_prediction_*`, `cdp_*_alert_*`

### Reports & Query Language (30 tools)

Manage dashboards, widgets, cubic set definitions, report definitions, cube metadata, and execute QL queries.

Tool prefix: `cdp_*_widget_*`, `cdp_*_dashboard_*`, `cdp_*_cubic_set_*`, `cdp_*_report_def_*`, `cdp_*_cube_*`, `cdp_*_ql_*`

### Cache, Security & Global Actions (16 tools)

Cache invalidation, security/authentication management, and global platform actions.

Tool prefix: `cdp_*_cache_*`, `cdp_*_security_*`, `cdp_*_global_*`

---

## 8. Available Resources

The server provides 8 read-only MCP resources accessible via URI patterns:

| Resource URI | Description |
|-------------|-------------|
| `cdp://tenant/{tenant_id}/resources` | Data warehouse entity types |
| `cdp://tenant/{tenant_id}/roles` | Available roles |
| `cdp://tenant/{tenant_id}/workflows` | Tenant workflows |
| `cdp://tenant/{tenant_id}/clusters` | Compute clusters |
| `cdp://tenant/{tenant_id}/udmp-tables` | UDMP table schemas |
| `cdp://tenant/{tenant_id}/cube-metadata` | OLAP cube metadata |
| `cdp://tenant/{tenant_id}/connector-templates` | Connector templates |
| `cdp://tenant/{tenant_id}/campaigns` | Campaign definitions |

Resources are read automatically by MCP clients for context. Replace `{tenant_id}` with your actual tenant ID.

---

## 9. Troubleshooting

### Server won't start

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'cdp_mcp'` | Run `pip install -e .` from the project root |
| `command not found: cdp-mcp` | Activate your virtual environment: `source .venv/bin/activate` |
| `requires-python >= 3.11` error | Upgrade Python to 3.11 or newer |

### Authentication errors

| Symptom | Fix |
|---------|-----|
| `401 Unauthorized` | Verify `CDP_CLIENT_ID`, `CDP_CLIENT_SECRET`, `CDP_USERNAME`, `CDP_PASSWORD` are correct |
| Token expired (static mode) | Rotate `CDP_AUTH_TOKEN` with a fresh token |
| `Connection refused` | Check `CDP_ENVIRONMENT` points to the right base URL |

### Client can't connect

| Symptom | Fix |
|---------|-----|
| Client shows "server not found" | Use the full absolute path to the `cdp-mcp` binary in client config |
| Tools not appearing | Restart the MCP client after config changes |
| Timeout errors | Ensure network access to CDP API endpoints is available |

### Debugging tips

1. **Test the server directly:**
   ```bash
   echo '{}' | cdp-mcp 2>/dev/null
   ```
   If it hangs waiting for input — the server is running correctly.

2. **Check `.env` is loaded:**
   Ensure your `.env` file is in the **current working directory** when launching the server.

3. **Use MCP Inspector:**
   ```bash
   npx @modelcontextprotocol/inspector cdp-mcp
   ```
   Browse tools and test individual calls interactively.

4. **Verbose logging:**
   Run with `stderr` visible to see any Python tracebacks:
   ```bash
   cdp-mcp 2>&1 | head -50
   ```

---

## Quick Start Cheat Sheet

```bash
# 1. Clone & install
git clone <repo-url> cdp-mcp && cd cdp-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Configure
cp .env.example .env
# Edit .env with your credentials

# 3. Test
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | cdp-mcp

# 4. Connect to Claude Desktop / VS Code (see Section 5)
```
