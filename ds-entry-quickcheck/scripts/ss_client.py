"""Minimal MCP (streamable HTTP) clients for SellerSprite and SIF.

Endpoint URLs (they embed the secret keys) are read at runtime from ~/.claude.json
(mcpServers.<name>.url) or the <NAME>_MCP_URL env var. They are never written to disk,
printed, or included in error messages.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import httpx

CACHE_DIR = Path.home() / ".cache" / "ds-entry-quickcheck"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _endpoint(server: str) -> str:
    url = os.environ.get(f"{server.upper()}_MCP_URL", "").strip()
    if url:
        return url
    cfg = json.loads((Path.home() / ".claude.json").read_text(encoding="utf-8"))
    try:
        return cfg["mcpServers"][server]["url"]
    except KeyError:
        raise SystemExit(f"MCP server '{server}' is not configured in ~/.claude.json (mcpServers.{server}.url)")


class McpClient:
    server = ""

    def __init__(self, min_interval: float = 2.0, timeout: float = 60.0, use_cache: bool = True):
        self._url = _endpoint(self.server)
        self._client = httpx.Client(timeout=timeout)
        self._session: str | None = None
        self._id = 0
        self._last = 0.0
        self._min_interval = min_interval
        self._use_cache = use_cache
        self._ready = False
        self.calls = 0
        self.cache_hits = 0

    # ------------------------------------------------------------------ transport
    def _headers(self) -> dict:
        h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self._session:
            h["Mcp-Session-Id"] = self._session
        return h

    def _post(self, payload: dict) -> dict | None:
        try:
            r = self._client.post(self._url, headers=self._headers(), json=payload)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:          # message would contain the URL -> strip it
            raise RuntimeError(f"{self.server} HTTP {e.response.status_code}") from None
        except httpx.HTTPError as e:
            raise RuntimeError(f"{self.server} network error: {type(e).__name__}") from None
        if sid := r.headers.get("mcp-session-id"):
            self._session = sid
        if not r.content:
            return None
        if "text/event-stream" in r.headers.get("content-type", ""):
            data = [ln[5:].strip() for ln in r.text.splitlines() if ln.startswith("data:")]
            return json.loads(data[-1]) if data else None
        return r.json()

    def _rpc(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        msg = self._post({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}})
        if msg is None:
            raise RuntimeError(f"empty response for {method}")
        if "error" in msg:
            raise RuntimeError(f"{method} error: {msg['error'].get('message', msg['error'])}")
        return msg["result"]

    def _initialize(self) -> None:
        if self._ready:
            return
        self._rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                 "clientInfo": {"name": "ds-entry-quickcheck", "version": "1.0"}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self._ready = True

    # ------------------------------------------------------------------ public
    def call(self, tool: str, args: dict, retries: int = 6) -> dict:
        """Call a tool; return the parsed payload {code, message, data}. Successful results are cached."""
        key = hashlib.sha1(json.dumps([tool, args], sort_keys=True).encode()).hexdigest()
        cache_file = CACHE_DIR / f"{self.server}_{tool}_{key}.json"
        if self._use_cache and cache_file.exists():
            self.cache_hits += 1
            return json.loads(cache_file.read_text(encoding="utf-8"))
        self._initialize()
        for attempt in range(retries):
            wait = self._min_interval - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            try:
                res = self._rpc("tools/call", {"name": tool, "arguments": args})
            except RuntimeError:
                if attempt == retries - 1:
                    raise
                time.sleep(2 * (attempt + 1))
                continue
            self.calls += 1
            text = "".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                raise RuntimeError(f"{tool}: non-JSON response: {text[:120]}") from None
            code = payload.get("code") if isinstance(payload, dict) else None
            if code == "ERROR_MAXIMUM_ACCESS_PER_MINUTE":
                print(f"    [rate limit] {tool}: waiting 65s", flush=True)
                time.sleep(65)
                continue
            if code not in ("OK", None):
                raise RuntimeError(f"{tool}: {code} {payload.get('message')}")
            cache_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            return payload
        raise RuntimeError(f"{tool}: gave up after {retries} attempts")


class SellerSprite(McpClient):
    server = "sellersprite"


class Sif(McpClient):
    server = "sif"
