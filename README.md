# CDP MCP Server

An MCP (Model Context Protocol) server that puts the Acquia **Customer Data Platform** at your LLM's fingertips. Point Claude, Copilot, or any MCP-aware client at this server and it can read your tenants, drive campaigns, poke at workflows, query reports, and generally do the boring admin work so you don't have to.

Built because clicking through CDP screens at 2 AM isn't anyone's idea of fun.

---

## What you get

- **~300 tools** spanning permissions, the data warehouse, campaigns, config, connectors, reports, predictions, mailer, emailable pages, segments, security, cache, and status APIs
- **8 playbook resources** that teach the LLM how to sequence real multi-step flows (campaign wizard, C360 profile render, workflow authoring, connector onboarding, UDMP schema edits, etc.) — these came from reverse-engineering the Vega and Config UIs so the model stops guessing
- **Two auth modes**: OAuth2 password grant (auto-refreshed, 401-retried, lock-serialized) or a static bearer token if you already have one
- **Dev / QA / Prod** switch via a single `CDP_ENVIRONMENT` variable
- Stdio transport, so it drops straight into Claude Desktop, VS Code Copilot, Continue, mcphost, Open WebUI (via supergateway), or MCP Inspector

If the above sounds like alphabet soup, skim [`TUTORIAL.md`](./TUTORIAL.md) — it walks through every piece with copy-pasteable commands.

---

## Quick start

```bash
# 1. Clone and install
git clone https://github.com/atharva-joshi77/cdp-mcp.git
cd cdp-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Configure
cp .env.example .env
# edit .env: CDP_ENVIRONMENT, CDP_TENANT_ID, and either
#   CDP_CLIENT_ID/SECRET + CDP_USERNAME/PASSWORD  (OAuth2)
# or CDP_AUTH_TOKEN                                (static token)

# 3. Run
cdp-mcp
```

`cdp-mcp` speaks JSON-RPC on stdio, so running it bare will look like it's hanging — that's correct. Wire it to an MCP client (see below) and it'll spring to life.

### Wire it to Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cdp": {
      "command": "/absolute/path/to/cdp-mcp/.venv/bin/cdp-mcp",
      "env": {
        "CDP_ENVIRONMENT": "dev",
        "CDP_TENANT_ID": "12345",
        "CDP_CLIENT_ID": "...",
        "CDP_CLIENT_SECRET": "...",
        "CDP_USERNAME": "...",
        "CDP_PASSWORD": "..."
      }
    }
  }
}
```

Restart Claude, and you should see ~300 `cdp_*` tools show up in the tool picker. For VS Code, Continue, Ollama/Open WebUI, and MCP Inspector setups, the full recipes are in [`TUTORIAL.md §5`](./TUTORIAL.md#5-connecting-to-an-mcp-client).

---

## Requirements

| Thing   | Minimum |
|---------|---------|
| Python  | 3.11+   |
| pip     | 23.0+   |
| A CDP tenant with API credentials | yes, sorry |

Dependencies (installed automatically):

- `mcp>=1.13.0` — FastMCP framework
- `httpx>=0.27.0` — async HTTP
- `pydantic` + `pydantic-settings` — config + validation
- `python-dotenv` — `.env` loading

---

## Project layout

```
src/cdp_mcp/
├── __main__.py           # entry point: `cdp-mcp` / `python -m cdp_mcp`
├── server.py             # FastMCP server, registers tools + resources
├── config.py             # env/.env loader
├── auth/                 # OAuth2 + static-token provider
├── utils/                # shared httpx client, error helpers
├── resources/            # MCP resource URIs (tenant/*, docs/*)
├── docs/                 # the eight playbooks, shipped as resources
├── types/                # pydantic request/response models
└── tools/                # one subpackage per CDP service area
    ├── permissions/      users, roles, clients
    ├── dw/               data warehouse, A360, audiences, offers, trackers
    ├── campaign/         defs, audiences, messages, dispatches, runs, exports
    ├── config_api/       tenants, workflows, schedules, UDMP, DQE, clusters…
    ├── connectors/       input + output connectors, templates
    ├── reports/          dashboards, widgets, cubes, QL
    ├── predictions/      prediction defs + content templates
    ├── mailer/           accounts, subusers, identifiers, batches
    ├── emailable_pages/  emailable-pages CRUD
    ├── security/         token, auth, SSO, password reset
    ├── cache/            cache ops
    ├── spam/             spam score
    ├── status/           status + orchestration/purge status
    ├── provisions/       self-service provisioning
    ├── global_actions/   platform-wide actions
    └── alerts/           stub (real Alerts API lives in a different stack)
```

Every tool shares a single `HttpClient` with pooled httpx connections, a shared auth token cache, an `asyncio.Lock` around refreshes, one-shot 401 retry, URL-encoded tenant IDs, and `logger.info` request/response tracing. If something feels off, the logs usually tell the truth.

---

## Playbooks (the secret sauce)

Tool lists alone aren't enough — a lot of CDP flows are "POST a def, then POST `?action=publish`, then GET status, then maybe POST `?action=schedule` with a separate schedule id." The LLM routinely gets this wrong if left to its own devices.

So the server ships eight Markdown playbooks as MCP resources:

| Resource | What it covers |
|----------|----------------|
| `cdp://docs/campaign-playbook` | Full Vega campaign-wizard lifecycle, folderId rules, batch vs triggered publish, datasetDef copy recovery, data-export save→run, async audience sizing |
| `cdp://docs/orchestration-playbook` | Schedule CRUD, connector/report/export/campaign runs, sQueryDef validate→save, provisioner, compaction, drain-before-delete |
| `cdp://docs/customer360-playbook` | Three-parallel-fetch profile load, layout deep-merge, realtime polling, `fq` search encoding, GDPR purge |
| `cdp://docs/admin-ops-playbook` | DQE batch writes, A360 three-phase saves, status-page job control, GDPR admin override |
| `cdp://docs/reports-dashboards-playbook` | Array-wrap POST, cube metadata walk, ad-hoc vs cached execute, dual freshness check |
| `cdp://docs/workflow-authoring-playbook` | symbolic workflowId vs numeric workflowDBId, graph load, step + edge batching, verb taxonomy |
| `cdp://docs/connector-wizard-playbook` | Input/output connector split, 4-or-5 step wizard, the `referenceId` vs `entityId` schedule trap |
| `cdp://docs/udmp-metadata-playbook` | Nested-read/flat-write shapes, cascade, publish ordering, custom-attribute whitelist |

MCP clients auto-discover them on connect, and the server `instructions` block points the model at each one.

---

## Authentication notes

- **OAuth2** (preferred): the provider hits `POST {baseUrl}/token?action=create` with credentials in headers, caches the token in memory, serializes concurrent refreshes behind an `asyncio.Lock`, and refreshes ~60s before expiry. Any `401` from a downstream call triggers a one-shot forced refresh + retry.
- **Static token**: set `CDP_AUTH_TOKEN` and the OAuth2 path is skipped entirely. You're on the hook for rotation.

Never put real secrets in this repo. `.env` is gitignored.

---

## Development

```bash
# smoke test: should print the server's capabilities + tool list
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}' | cdp-mcp

# interactive tool browser
npx @modelcontextprotocol/inspector cdp-mcp

# verify tool count
python3 -c "from cdp_mcp.server import create_server; import asyncio; \
  print(len(asyncio.run(create_server().list_tools())))"
```

There's a fuller troubleshooting matrix (server-won't-start, 401s, client-can't-connect, etc.) in [`TUTORIAL.md §9`](./TUTORIAL.md#9-troubleshooting). The full remediation history and endpoint coverage audit lives in [`MCP_AUDIT.md`](./MCP_AUDIT.md) if you want to understand *why* things are wired the way they are.

---

## Status

- Tool count: **301** across 12 CDP services
- Playbook resources: **8**
- All P0 / P1 / P2 audit items from [`MCP_AUDIT.md`](./MCP_AUDIT.md) resolved
- Alerts tools are intentionally stubbed — the real Alerts API lives on a separate MuleSoft/Go stack that needs its own base URL and auth (PRs welcome)
- Integration test harness is a work in progress (scaffolding present, full contract coverage tracked as follow-up)

---

## Contributing

1. Fork, branch, hack.
2. Run `./gradlew-equivalent` — fine, just `pip install -e .` and the smoke test above.
3. If you add a tool, wire it into the matching `tools/<area>/__init__.py` registrar.
4. If you add a multi-step flow, write a playbook for it under `src/cdp_mcp/docs/` and register the resource in `resources/resource_providers.py`.
5. Open a PR. Be nice in the description.

---

## License

Internal / proprietary — check with Acquia before using this outside your own tenant.

---

Built with equal parts `httpx`, `pydantic`, and spite for flaky CDP wizards.

