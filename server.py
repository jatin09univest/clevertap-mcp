#!/usr/bin/env python3
"""CleverTap MCP Server — exposes CleverTap REST API as MCP tools for Univest analytics."""

import json
import os
import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

ACCOUNT_ID = os.environ.get("CLEVERTAP_ACCOUNT_ID")
PASSCODE = os.environ.get("CLEVERTAP_PASSCODE")
BASE_URL = os.environ.get("CLEVERTAP_BASE_URL", "https://eu1.api.clevertap.com")

if not ACCOUNT_ID or not PASSCODE:
    raise RuntimeError(
        "CleverTap credentials missing. Set CLEVERTAP_ACCOUNT_ID and "
        "CLEVERTAP_PASSCODE in the environment (see README)."
    )

HEADERS = {
    "X-CleverTap-Account-Id": ACCOUNT_ID,
    "X-CleverTap-Passcode": PASSCODE,
    "Content-Type": "application/json",
}

app = Server("clevertap")


async def ct_post(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE_URL}{path}", headers=HEADERS, json=body)
        r.raise_for_status()
        return r.json()


async def ct_get(path: str, params: dict = None) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{BASE_URL}{path}", headers=HEADERS, params=params)
        r.raise_for_status()
        return r.json()


@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="clevertap_get_profiles_by_event",
            description=(
                "Fetch user profiles who performed a specific event in a date range. "
                "Returns identity, platform, country, and profile properties. "
                "Use cursor from response to paginate further results."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "event_name": {
                        "type": "string",
                        "description": "CleverTap event name e.g. 'App Uninstalled', 'Charged'",
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date in YYYYMMDD format e.g. '20260101'",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in YYYYMMDD format e.g. '20260430'",
                    },
                    "batch_size": {
                        "type": "integer",
                        "description": "Profiles per page (max 100). Default 50.",
                        "default": 50,
                    },
                    "cursor": {
                        "type": "string",
                        "description": "Pagination cursor returned from a previous call.",
                    },
                },
                "required": ["event_name", "from_date", "to_date"],
            },
        ),
        types.Tool(
            name="clevertap_get_event_count",
            description=(
                "Get the total count of times an event occurred in a date range, "
                "optionally filtered by property conditions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "event_name": {
                        "type": "string",
                        "description": "CleverTap event name",
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date YYYYMMDD",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date YYYYMMDD",
                    },
                },
                "required": ["event_name", "from_date", "to_date"],
            },
        ),
        types.Tool(
            name="clevertap_get_dau",
            description="Get Daily Active Users (DAU) for a date range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date YYYYMMDD",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date YYYYMMDD",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
        types.Tool(
            name="clevertap_get_top_events",
            description="Get the top events by occurrence count for a date range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date YYYYMMDD",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date YYYYMMDD",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
        types.Tool(
            name="clevertap_get_profile",
            description="Get the full profile of a single user by their CleverTap identity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "identity": {
                        "type": "string",
                        "description": "User identity (email, phone, or custom ID)",
                    },
                },
                "required": ["identity"],
            },
        ),
        types.Tool(
            name="clevertap_get_event_trend",
            description=(
                "Get day-by-day trend (counts) for an event over a date range. "
                "Useful for spotting spikes or drops around a release."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "event_name": {
                        "type": "string",
                        "description": "CleverTap event name",
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date YYYYMMDD",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date YYYYMMDD",
                    },
                },
                "required": ["event_name", "from_date", "to_date"],
            },
        ),
        types.Tool(
            name="clevertap_get_uninstall_report",
            description=(
                "Get app uninstall counts per day. Returns a date-keyed report "
                "of uninstall events for the specified range."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date YYYYMMDD",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date YYYYMMDD",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "clevertap_get_profiles_by_event":
            result = await _get_profiles_by_event(arguments)
        elif name == "clevertap_get_event_count":
            result = await _get_event_count(arguments)
        elif name == "clevertap_get_dau":
            result = await _get_dau(arguments)
        elif name == "clevertap_get_top_events":
            result = await _get_top_events(arguments)
        elif name == "clevertap_get_profile":
            result = await _get_profile(arguments)
        elif name == "clevertap_get_event_trend":
            result = await _get_event_trend(arguments)
        elif name == "clevertap_get_uninstall_report":
            result = await _get_uninstall_report(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
    except httpx.HTTPStatusError as e:
        result = {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        result = {"error": str(e)}

    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def _get_profiles_by_event(args: dict) -> dict:
    if "cursor" in args and args["cursor"]:
        return await ct_get("/1/profiles.json", params={"cursor": args["cursor"]})

    body = {
        "event_name": args["event_name"],
        "from": args["from_date"],
        "to": args["to_date"],
        "batch_size": args.get("batch_size", 50),
    }
    return await ct_post("/1/profiles.json", body)


async def _get_event_count(args: dict) -> dict:
    body = {
        "event_name": args["event_name"],
        "from": args["from_date"],
        "to": args["to_date"],
    }
    return await ct_post("/1/counts/events.json", body)


async def _get_dau(args: dict) -> dict:
    return await ct_get("/1/counts/dau.json", params={
        "from": args["from_date"],
        "to": args["to_date"],
    })


async def _get_top_events(args: dict) -> dict:
    return await ct_get("/1/counts/topevents.json", params={
        "from": args["from_date"],
        "to": args["to_date"],
    })


async def _get_profile(args: dict) -> dict:
    return await ct_get("/1/profile.json", params={"identity": args["identity"]})


async def _get_event_trend(args: dict) -> dict:
    body = {
        "event_name": args["event_name"],
        "from": args["from_date"],
        "to": args["to_date"],
    }
    return await ct_post("/1/counts/events.json", body)


async def _get_uninstall_report(args: dict) -> dict:
    return await ct_get("/1/counts/uninstalls.json", params={
        "from": args["from_date"],
        "to": args["to_date"],
    })


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
