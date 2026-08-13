#!/usr/bin/env python3
"""Read-only Home Assistant MCP server (stdlib only)."""

import datetime
import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

TIMEOUT = 10


class HAClient:
    def __init__(self, host: str, port: str, api_key: str) -> None:
        self.base_url = f"http://{host}:{port}/api"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def get(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise

    def get_text(self, path: str) -> str:
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read().decode()

    def post(self, path: str, body: dict) -> Any:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers=self.headers, method="POST")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read().decode()


def ha_get_state(client: HAClient, entity_id: str) -> str:
    result = client.get(f"/states/{entity_id}")
    if result is None:
        return f"Entity not found: {entity_id}"
    return json.dumps(result, indent=2)


def ha_list_states(client: HAClient, domain: str | None = None) -> str:
    states = client.get("/states")
    if domain:
        states = [s for s in states if s["entity_id"].startswith(f"{domain}.")]
    slim = [
        {
            "entity_id": s["entity_id"],
            "state": s["state"],
            "friendly_name": s.get("attributes", {}).get("friendly_name", ""),
        }
        for s in states
    ]
    return json.dumps(slim, indent=2)


def ha_search_entities(client: HAClient, query: str) -> str:
    states = client.get("/states")
    q = query.lower()
    matches = []
    for s in states:
        eid = s["entity_id"].lower()
        fname = s.get("attributes", {}).get("friendly_name", "").lower()
        if q in eid or q in fname:
            matches.append(
                {
                    "entity_id": s["entity_id"],
                    "state": s["state"],
                    "friendly_name": s.get("attributes", {}).get("friendly_name", ""),
                }
            )
        if len(matches) >= 50:
            break
    return json.dumps(matches, indent=2)


def ha_render_template(client: HAClient, template: str) -> str:
    return client.post("/template", {"template": template})


def ha_get_logbook(client: HAClient, entity_id: str | None = None, hours: int = 1) -> str:
    hours = max(1, min(24, hours))
    now = datetime.datetime.now(datetime.timezone.utc)
    start = now - datetime.timedelta(hours=hours)
    start_iso = start.isoformat()
    params: dict = {"end_time": now.isoformat()}
    if entity_id:
        params["entity"] = entity_id
    qs = urllib.parse.urlencode(params)
    result = client.get(f"/logbook/{urllib.parse.quote(start_iso, safe='')}?{qs}")
    if not result:
        return "No logbook entries found."
    return json.dumps(result, indent=2)


def ha_get_error_log(client: HAClient) -> str:
    return client.get_text("/error_log")


def ha_get_history(
    client: HAClient,
    entity_ids: str,
    hours: int = 1,
    significant_changes_only: bool = True,
) -> str:
    hours = max(1, min(24, hours))
    now = datetime.datetime.now(datetime.timezone.utc)
    start = now - datetime.timedelta(hours=hours)
    start_iso = start.isoformat()
    params: dict = {
        "filter_entity_id": entity_ids,
        "end_time": now.isoformat(),
        "minimal_response": "true",
        "no_attributes": "true",
    }
    if significant_changes_only:
        params["significant_changes_only"] = "true"
    qs = urllib.parse.urlencode(params)
    result = client.get(f"/history/period/{urllib.parse.quote(start_iso, safe='')}?{qs}")
    if not result:
        return "No history found."
    return json.dumps(result, indent=2)


def ha_get_services(client: HAClient, domain: str | None = None) -> str:
    services = client.get("/services")
    if domain:
        services = [s for s in services if s.get("domain") == domain]
    return json.dumps(services, indent=2)


TOOLS = [
    {
        "name": "ha_get_state",
        "description": "Get the full state and attributes of a Home Assistant entity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Entity ID, e.g. light.living_room"}
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "ha_list_states",
        "description": "List all entity states, optionally filtered by domain. Returns slim records (entity_id, state, friendly_name).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Optional domain filter, e.g. light, switch, sensor"}
            },
        },
    },
    {
        "name": "ha_search_entities",
        "description": "Search entities by entity_id or friendly_name (case-insensitive). Returns up to 50 matches.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search string to match against entity_id and friendly_name"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "ha_render_template",
        "description": "Render a Jinja2 template using the live Home Assistant state.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template": {"type": "string", "description": "Jinja2 template string to evaluate"}
            },
            "required": ["template"],
        },
    },
    {
        "name": "ha_get_services",
        "description": "List available Home Assistant services, optionally filtered by domain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Optional domain filter, e.g. light, switch"}
            },
        },
    },
    {
        "name": "ha_get_logbook",
        "description": "Fetch Home Assistant logbook entries (state changes, automation triggers, service calls). Useful for debugging automations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Optional entity ID to filter entries, e.g. automation.exterior_doors"},
                "hours": {"type": "integer", "description": "How many hours back to fetch (1–24, default 1)"},
            },
        },
    },
    {
        "name": "ha_get_error_log",
        "description": "Fetch the Home Assistant error log (plaintext). Useful for diagnosing integration errors and warnings.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ha_get_history",
        "description": "Fetch state change history for one or more entities over a time window.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_ids": {"type": "string", "description": "Comma-separated entity IDs, e.g. binary_sensor.front_door,light.living_room"},
                "hours": {"type": "integer", "description": "How many hours back to fetch (1–24, default 1)"},
                "significant_changes_only": {"type": "boolean", "description": "Only return significant state changes (default true)"},
            },
            "required": ["entity_ids"],
        },
    },
]


class MCPServer:
    def __init__(self, client: HAClient) -> None:
        self.client = client

    def run(self) -> None:
        log.info("MCP server started")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                log.error("Failed to parse JSON: %s", e)
                continue

            method = request.get("method", "")
            req_id = request.get("id")

            # Notifications have no id — no response needed
            if req_id is None:
                log.info("Notification: %s", method)
                continue

            response = self._handle(req_id, method, request.get("params", {}))
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

    def _handle(self, req_id: Any, method: str, params: dict) -> dict:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "homeassistant", "version": "1.0.0"},
                },
            }

        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

        if method == "tools/call":
            return self._call_tool(req_id, params.get("name", ""), params.get("arguments", {}))

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    def _call_tool(self, req_id: Any, name: str, args: dict) -> dict:
        def ok(text: str) -> dict:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": text}]},
            }

        def err(text: str) -> dict:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": text}], "isError": True},
            }

        try:
            if name == "ha_get_state":
                return ok(ha_get_state(self.client, args["entity_id"]))
            if name == "ha_list_states":
                return ok(ha_list_states(self.client, args.get("domain")))
            if name == "ha_search_entities":
                return ok(ha_search_entities(self.client, args["query"]))
            if name == "ha_render_template":
                return ok(ha_render_template(self.client, args["template"]))
            if name == "ha_get_services":
                return ok(ha_get_services(self.client, args.get("domain")))
            if name == "ha_get_logbook":
                return ok(ha_get_logbook(self.client, args.get("entity_id"), int(args.get("hours", 1))))
            if name == "ha_get_error_log":
                return ok(ha_get_error_log(self.client))
            if name == "ha_get_history":
                return ok(ha_get_history(
                    self.client,
                    args["entity_ids"],
                    int(args.get("hours", 1)),
                    bool(args.get("significant_changes_only", True)),
                ))
            return err(f"Unknown tool: {name}")
        except Exception as e:
            log.error("Tool %s failed: %s", name, e)
            return err(f"Error calling {name}: {e}")


def main() -> None:
    api_key = os.environ.get("HOMEASSISTANT_API_KEY")
    if not api_key:
        log.error("HOMEASSISTANT_API_KEY is not set")
        sys.exit(1)

    host = os.environ.get("HA_HOST", "homeassistant.local")
    port = os.environ.get("HA_PORT", "8123")

    client = HAClient(host, port, api_key)
    MCPServer(client).run()


if __name__ == "__main__":
    main()
