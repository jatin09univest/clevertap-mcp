# CleverTap MCP — Univest Analytics

An [MCP](https://modelcontextprotocol.io) server that exposes the **CleverTap analytics REST API** as tools your AI agent (Claude Code, Cursor, etc.) can call directly. Ask questions about users, events, retention, and uninstalls in plain English — the agent pulls live numbers from CleverTap for you.

> **Univest team:** this queries the same CleverTap account that powers the app's analytics. Credentials are supplied via environment variables — **never** commit them.

---

## Why use this

| Without the MCP | With the MCP |
|---|---|
| Log into the CleverTap dashboard, click through Events → Trends → filters | Ask *"what's the DAU trend for the last 14 days?"* and get numbers |
| Copy/paste event names, guess date formats | Agent knows the tool schemas and formats requests correctly |
| Export CSVs and eyeball them | Agent computes, compares, and explains the data inline |
| Analytics lives in one person's head | Any teammate with the repo + passcode can query it |

**Concretely, you can:**
- 📊 Pull **event counts / trends** (`Charged`, `App Launched`, custom events) over any date range
- 👤 Look up a **single user's full profile** by CleverTap identity
- 🔁 List **who performed an event** (e.g. everyone who `App Uninstalled` last week)
- 📉 Get **uninstall reports** and **DAU** to track retention
- 🏆 See **top events** by volume to understand what users actually do
- 💬 Do all of the above **conversationally**, chained with your own analysis

---

## Tools

| Tool | What it does |
|---|---|
| `clevertap_get_dau` | Daily Active Users for a date range |
| `clevertap_get_top_events` | Top events by occurrence count for a date range |
| `clevertap_get_event_count` | Total count of an event in a range, optionally filtered by property conditions |
| `clevertap_get_event_trend` | Day-by-day trend for a single event |
| `clevertap_get_uninstall_report` | App uninstall counts per day |
| `clevertap_get_profile` | Full profile of one user by CleverTap identity |
| `clevertap_get_profiles_by_event` | Profiles of users who performed an event in a range (paginated via cursor) |

Dates use `YYYYMMDD` format (e.g. `20260101`). The agent handles this for you — just say "last 7 days".

---

## Setup

### 1. Requirements
- Python 3.10+
- A CleverTap account **ID** and **passcode** (Dashboard → Settings → Engagement → API)

### 2. Clone & install
```sh
git clone -b jatin https://github.com/jatin09univest/clevertap-mcp.git ~/clevertap-mcp
cd ~/clevertap-mcp
pip install -r requirements.txt
```

### 3. Register with Claude Code
```sh
claude mcp add clevertap python3 ~/clevertap-mcp/server.py \
  -e CLEVERTAP_ACCOUNT_ID=YOUR_ACCOUNT_ID \
  -e CLEVERTAP_PASSCODE=YOUR_PASSCODE
```

Or add it to a project's `.mcp.json` (shared via git — safe because secrets stay in your shell):
```json
{
  "mcpServers": {
    "clevertap": {
      "type": "stdio",
      "command": "python3",
      "args": ["/absolute/path/to/clevertap-mcp/server.py"],
      "env": {
        "CLEVERTAP_ACCOUNT_ID": "${CLEVERTAP_ACCOUNT_ID}",
        "CLEVERTAP_PASSCODE": "${CLEVERTAP_PASSCODE}"
      }
    }
  }
}
```

### Environment variables

| Variable | Required | Default | Notes |
|---|---|---|---|
| `CLEVERTAP_ACCOUNT_ID` | ✅ | — | From CleverTap → Settings → Engagement |
| `CLEVERTAP_PASSCODE` | ✅ | — | Keep secret. Share via 1Password/Slack DM, never git |
| `CLEVERTAP_BASE_URL` | ❌ | `https://eu1.api.clevertap.com` | Change region if your account isn't on EU (e.g. `https://us1.api.clevertap.com`) |

The server **refuses to start** if the ID or passcode is missing.

---

## Usage examples

Once registered, just talk to your agent:

- *"What was our DAU each day last week?"* → `clevertap_get_dau`
- *"How many `Charged` events fired in June 2026?"* → `clevertap_get_event_count`
- *"Show the daily trend for `App Launched` over the last 14 days."* → `clevertap_get_event_trend`
- *"Which users uninstalled in the last 3 days?"* → `clevertap_get_profiles_by_event`
- *"Pull the full profile for CleverTap identity `98765`."* → `clevertap_get_profile`
- *"What are our top 10 events this month?"* → `clevertap_get_top_events`

The agent picks the right tool, formats the dates, calls CleverTap, and explains the result.

---

## Security

- 🔒 **No credentials in this repo.** They come from env vars only; the server errors out without them.
- 🚫 Never paste the passcode into code, chat logs, or commits — it grants full access to your CleverTap account.
- 🔑 Rotate the passcode in the CleverTap dashboard if it's ever exposed.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `CleverTap credentials missing` on start | Set `CLEVERTAP_ACCOUNT_ID` and `CLEVERTAP_PASSCODE` in the MCP `env` block |
| `401 Unauthorized` from CleverTap | Wrong passcode, or account is on a different region — check `CLEVERTAP_BASE_URL` |
| Empty results | Event name is case-sensitive; confirm it matches the dashboard exactly |
| `ModuleNotFoundError: mcp` / `httpx` | Run `pip install -r requirements.txt` |
