#!/usr/bin/env python3
"""api_client — the ONE way the product calls another app's API. Every call gets, without the caller thinking about it:

  - a timeout (no call hangs a run);
  - retries only where a retry can help (429 and 5xx, a dropped connection), waiting what the provider asks
    (`Retry-After`) or an exponential back-off with jitter, never more than 30 s, never more than `retries` times;
  - a circuit breaker per provider: after 5 failures in a row the provider is left alone for 10 minutes, so a broken
    API costs one error line, not a thousand calls;
  - a cache for GET calls with a time to live, so the same answer is not paid for twice (the cheapest call is none);
  - one usage line per call in data/api_usage.jsonl (provider, method, path, status, milliseconds, bytes, cached,
    attempt) — the real usage the weekly review compares with each provider's limit (tools/api_usage.py).

Keys are never written in code or in a chat: pass the NAME of an environment variable (`key_env`), which the code
host's secret store fills in the publishing run. Every provider called here has an entry in docs/APPS.yaml.

    from api_client import call
    r = call("ticketing", "https://api.example.com/v2/events.json?city=Austin", key_env="EXAMPLE_KEY", key_param="apikey", cache_ttl=3600)
    r.status, r.json(), r.from_cache
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("KIT_API_DATA", ROOT / "data"))
RETRY_STATUS = {429, 500, 502, 503, 504}
OPEN_AFTER, OPEN_FOR_S, MAX_WAIT_S = 5, 600, 30


class CircuitOpen(RuntimeError):
    """The provider failed too often just now; it is left alone until the circuit closes."""


@dataclass
class Response:
    status: int
    body: bytes
    headers: dict = field(default_factory=dict)
    from_cache: bool = False

    def json(self):
        return json.loads(self.body or b"null")


def _now() -> float:
    return time.time()


def _circuit_path() -> Path:
    return DATA / "api_circuit.json"


def _circuit() -> dict:
    p = _circuit_path()
    return json.loads(p.read_text()) if p.is_file() else {}


def _save_circuit(c: dict) -> None:
    _circuit_path().parent.mkdir(parents=True, exist_ok=True)
    _circuit_path().write_text(json.dumps(c))


def _log(provider: str, method: str, url: str, status: int, ms: float, size: int, cached: bool, attempt: int) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    parts = urllib.parse.urlsplit(url)
    line = {"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "provider": provider, "method": method,
            "host": parts.netloc, "path": parts.path, "status": status, "ms": round(ms), "bytes": size,
            "cached": cached, "attempt": attempt}
    with (DATA / "api_usage.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


def _wait(attempt: int, retry_after: str | None, sleep) -> None:
    if retry_after and retry_after.strip().isdigit():
        seconds = min(float(retry_after), MAX_WAIT_S)
    else:
        seconds = min(MAX_WAIT_S, (2 ** attempt) * 0.5 + random.uniform(0, 0.5))
    sleep(seconds)


def call(provider: str, url: str, *, method: str = "GET", headers: dict | None = None, data: bytes | None = None,
         timeout: float = 20, retries: int = 3, cache_ttl: int = 0, key_env: str | None = None,
         key_param: str | None = None, key_header: str | None = None, sleep=time.sleep) -> Response:
    """Call an API the safe way. Raises CircuitOpen while the provider's circuit is open; returns the last Response
    (whatever its status) after the retries; raises the last connection error if no response ever came."""
    c = _circuit().get(provider, {})
    if c.get("open_until", 0) > _now():
        raise CircuitOpen(f"{provider}: {c.get('fails')} failures in a row; left alone until {time.ctime(c['open_until'])}")
    headers = dict(headers or {})
    if key_env:
        key = os.environ.get(key_env, "")
        if not key:
            raise RuntimeError(f"{provider}: the secret {key_env} is not set here (it lives in the code host's secret store)")
        if key_param:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode({key_param: key})
        else:
            headers[key_header or "Authorization"] = key if key_header else f"Bearer {key}"
    cache_file = None
    if method == "GET" and cache_ttl > 0:
        cache_key = hashlib.sha256((provider + " " + url.split(f"{key_param}=")[0] if key_param else provider + " " + url).encode()).hexdigest()
        cache_file = DATA / "api_cache" / f"{cache_key}.json"
        if cache_file.is_file():
            kept = json.loads(cache_file.read_text())
            if _now() - kept["at"] < cache_ttl:
                body = kept["body"].encode()
                _log(provider, method, url, kept["status"], 0, len(body), True, 0)
                return Response(kept["status"], body, kept.get("headers", {}), True)
    last_error: Exception | None = None
    resp: Response | None = None
    for attempt in range(retries + 1):
        start = _now()
        try:
            req = urllib.request.Request(url, data=data, method=method, headers={"User-Agent": "owner-run-kit", **headers})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = Response(r.status, r.read(), dict(r.headers))
        except urllib.error.HTTPError as e:
            resp = Response(e.code, e.read() if hasattr(e, "read") else b"", dict(e.headers or {}))
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last_error, resp = e, None
        ms = (_now() - start) * 1000
        safe_url = url.split(f"{key_param}=")[0] if key_param else url   # the key never reaches the log
        _log(provider, method, safe_url, resp.status if resp else 0, ms, len(resp.body) if resp else 0, False, attempt)
        retryable = resp is None or resp.status in RETRY_STATUS
        if not retryable or attempt == retries:
            break
        _wait(attempt, resp.headers.get("Retry-After") if resp else None, sleep)
    circuit = _circuit()
    failed = resp is None or resp.status in RETRY_STATUS
    state = circuit.get(provider, {"fails": 0})
    state["fails"] = state.get("fails", 0) + 1 if failed else 0
    if state["fails"] >= OPEN_AFTER:
        state["open_until"] = _now() + OPEN_FOR_S
    circuit[provider] = state
    _save_circuit(circuit)
    if resp is None:
        raise last_error or RuntimeError(f"{provider}: no response")
    if cache_file is not None and resp.status == 200:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps({"at": _now(), "status": resp.status, "headers": {}, "body": resp.body.decode("utf-8", "replace")}))
    return resp
