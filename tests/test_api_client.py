"""tools/api_client.py against a local server: it retries a 429 as told, opens the circuit after repeated failures,
answers a repeat from its cache, never writes the key to the usage log, and api_usage.py flags a failing provider."""
from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import api_client  # noqa: E402
import api_usage  # noqa: E402

PLAN: list[int] = []   # the statuses the server answers, in order; 200 once the list is empty
HITS: list[str] = []


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        HITS.append(self.path)
        status = PLAN.pop(0) if PLAN else 200
        body = json.dumps({"_embedded": {"events": [{"name": "A show"}]}}).encode()
        self.send_response(status)
        if status == 429:
            self.send_header("Retry-After", "0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


@pytest.fixture()
def server(tmp_path, monkeypatch):
    monkeypatch.setattr(api_client, "DATA", tmp_path)
    PLAN.clear(); HITS.clear()
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}", tmp_path
    httpd.shutdown()


def no_sleep(_):
    pass


def test_a_429_is_retried_as_told_then_answers(server):
    url, data = server
    PLAN.extend([429, 503])
    r = api_client.call("demo", url + "/events", sleep=no_sleep)
    assert r.status == 200 and len(HITS) == 3
    assert r.json()["_embedded"]["events"][0]["name"] == "A show"


def test_the_circuit_opens_after_repeated_failures(server):
    url, data = server
    PLAN.extend([500] * 40)
    for _ in range(api_client.OPEN_AFTER):
        assert api_client.call("flaky", url + "/x", retries=0, sleep=no_sleep).status == 500
    with pytest.raises(api_client.CircuitOpen):
        api_client.call("flaky", url + "/x", retries=0, sleep=no_sleep)
    assert len(HITS) == api_client.OPEN_AFTER   # the open circuit made no call


def test_a_repeat_comes_from_the_cache_and_the_key_is_never_logged(server, monkeypatch):
    url, data = server
    monkeypatch.setenv("DEMO_KEY", "s3cret-value")
    a = api_client.call("demo", url + "/e?city=x", key_env="DEMO_KEY", key_param="apikey", cache_ttl=3600, sleep=no_sleep)
    b = api_client.call("demo", url + "/e?city=x", key_env="DEMO_KEY", key_param="apikey", cache_ttl=3600, sleep=no_sleep)
    assert a.status == b.status == 200 and not a.from_cache and b.from_cache and len(HITS) == 1
    log = (data / "api_usage.jsonl").read_text()
    assert "s3cret-value" not in log and "s3cret-value" not in "".join(p.read_text() for p in (data / "api_cache").iterdir())


def test_a_missing_secret_is_said_plainly(server, monkeypatch):
    url, _ = server
    monkeypatch.delenv("NOT_SET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="secret store"):
        api_client.call("demo", url, key_env="NOT_SET_KEY")


def test_usage_flags_a_provider_that_fails_or_nears_its_limit():
    rows = [{"provider": "p", "status": 200, "ms": 100, "cached": False}] * 90 + \
           [{"provider": "p", "status": 429, "ms": 10, "cached": False}] * 10
    code, lines = api_usage.summarise(rows, {"p": 1000}, 1)
    assert code == 1 and "FAILED" in lines[0]
    code, lines = api_usage.summarise(rows[:90], {"p": 100}, 1)
    assert code == 1 and "OVER 80%" in lines[0]
    code, _ = api_usage.summarise(rows[:90], {"p": 10000}, 1)
    assert code == 0
