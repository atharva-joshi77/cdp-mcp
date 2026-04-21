"""One-off generator for SUPPORTED_TOOLS.md."""
import asyncio, os, re
from cdp_mcp.server import create_server
import cdp_mcp.tools as tools_pkg

name_to_file = {}
tools_root = os.path.dirname(tools_pkg.__file__)
for root, _, files in os.walk(tools_root):
    for f in files:
        if not f.endswith(".py"):
            continue
        p = os.path.join(root, f)
        try:
            txt = open(p).read()
        except Exception:
            continue
        for m in re.finditer(r'name\s*=\s*"(cdp_[a-zA-Z0-9_]+)"', txt):
            name_to_file.setdefault(m.group(1), os.path.relpath(p, tools_root))

s = create_server()
tools = asyncio.run(s.list_tools())

groups = {}
for t in tools:
    f = name_to_file.get(t.name, "unknown/unknown.py")
    area = f.split("/")[0]
    groups.setdefault(area, []).append(t)

AREA_TITLES = {
    "permissions": "Permissions — users, roles, clients",
    "dw": "Data Warehouse — entities, A360, audiences, offers, trackers, purge",
    "campaign": "Campaigns — definitions, audiences, messages, dispatches, runs, exports, templates",
    "config_api": "Config API — tenants, workflows, schedules, UDMP, DQE, clusters, connectors, mappings",
    "connectors": "Connectors — input/output connectors and connector templates",
    "reports": "Reports & Query — dashboards, widgets, cubes, sQueryDefs, report defs",
    "predictions": "Predictions & Content — prediction defs, templates, containers",
    "mailer": "Mailer — accounts, subusers, identifiers, batches",
    "emailable_pages": "Emailable Pages",
    "segments": "Segments",
    "security": "Security — token, authentication, SSO, password reset",
    "cache": "Cache operations",
    "spam": "Spam score",
    "status": "Status — job status, orchestration, purge",
    "provisions": "Self-Service Provisioning",
    "global_actions": "Global platform actions",
    "alerts": "Alerts (stubbed)",
}

ORDER = [
    "permissions", "dw", "campaign", "config_api", "connectors", "reports",
    "predictions", "mailer", "emailable_pages", "segments", "security",
    "cache", "spam", "status", "provisions", "global_actions", "alerts",
]

ordered = [a for a in ORDER if a in groups and groups[a]] + [
    a for a in groups if a not in ORDER and a != "unknown"
]

out = []
out.append("# Supported Tools")
out.append("")
out.append(
    f"This document lists every tool the `cdp-mcp` server registers with MCP clients. "
    f"**Total: {len(tools)} tools** across {len(ordered)} CDP service areas."
)
out.append("")
out.append(
    "Every tool accepts an optional `tenant_id` parameter. When omitted, the server "
    "falls back to the `CDP_TENANT_ID` set in your environment / `.env` file."
)
out.append("")
out.append(
    "> Tool names are the identifiers MCP clients display in their tool picker. "
    "Descriptions shown below are the one-liners exposed to the LLM to help it pick "
    "the right tool. For parameter-level detail, inspect the tool via MCP Inspector "
    "or read the source under `src/cdp_mcp/tools/`."
)
out.append("")
out.append("## Contents")
out.append("")
for a in ordered:
    title = AREA_TITLES.get(a, a.replace("_", " ").title())
    anchor = a.replace("_", "-")
    out.append(f"- [{title}](#{anchor}) — {len(groups[a])} tools")
out.append("")

for a in ordered:
    title = AREA_TITLES.get(a, a.replace("_", " ").title())
    anchor = a.replace("_", "-")
    out.append(f"## {title}")
    out.append("")
    out.append(f'<a id="{anchor}"></a>')
    out.append("")
    if a == "alerts":
        out.append(
            "> **Note:** Alert tools are currently stubbed. The legacy endpoints "
            "this module targeted no longer exist; the real Alerts API lives on a "
            "separate MuleSoft/Go stack that needs its own base URL and auth. "
            "`register_alert_tools()` is a no-op until that plumbing is wired up, "
            "so no tools from this area are active."
        )
        out.append("")
        continue
    out.append("| Tool | Description |")
    out.append("|------|-------------|")
    for t in sorted(groups[a], key=lambda x: x.name):
        desc = (t.description or "").strip().split("\n")[0].replace("|", "\\|")
        if len(desc) > 220:
            desc = desc[:217] + "..."
        out.append(f"| `{t.name}` | {desc} |")
    out.append("")

out.append("---")
out.append("")
out.append(
    "This file is generated from the live server via `_gen_tools.py`. Re-run it "
    "after adding or renaming tools:"
)
out.append("")
out.append("```bash")
out.append("python3 _gen_tools.py")
out.append("```")
out.append("")

with open("SUPPORTED_TOOLS.md", "w") as f:
    f.write("\n".join(out))

print(f"wrote SUPPORTED_TOOLS.md — {len(tools)} tools, {len(ordered)} areas")
for a in ordered:
    print(f"  {a}: {len(groups[a])}")

