#!/usr/bin/env python3
"""orders — the work orders: every value and button the finished product must show, what makes each done, and whether it is.

    python3 tools/orders.py plan               is the plan complete? exit 1 when a slot is empty, an id repeats, a
                                               `needs` names no order, a test cannot be run, or a named file is missing
    python3 tools/orders.py run [names]        run the tests. names: a file stem (Main), an order (Main.03) or "faults";
                                               none = all
        --site S                               the live address (default kit.json live_url) or a built folder (site/)
        --record                               write what was seen to work/seen.json (live address only)
    python3 tools/orders.py faults             what is wrong and not yet fixed, oldest first (exit 1 when there is any)
    python3 tools/orders.py count              orders passing on the live product, file by file

An order is done when its test passes on the live product. Nobody types a status: `run --record` writes it.
A failure is an order of kind `fault`: written with a test that fails, closed only by that test passing on the live
product. An order that passed once and fails now is a fault again, whatever its kind. work/ORDERS_FORMAT.md is the format.
Order files: work/*.yaml (needs PyYAML) or work/*.json, each a list of orders.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kitconf import CONF, ROOT  # noqa: E402

WORK = ROOT / "work"
SEEN = WORK / "seen.json"
SLOTS = ("id", "kind", "what", "from", "kept", "shown", "pass", "test", "how", "if_it_fails", "needs", "owner")
FAULT_SLOTS = ("found", "seen_how", "next")
TESTS = {"answers": (), "text": (), "count": (), "share": ("of", "with"), "bytes": ("at_most",),
         "command": ("run",), "person": ("proof",)}


# ------------------------------------------------------------------ reading the orders

def load_orders() -> list[dict]:
    out = []
    for path in sorted(WORK.glob("*")):
        if path.suffix in (".yaml", ".yml"):
            try:
                import yaml
            except ImportError:
                sys.exit(f"orders: {path.name} is YAML and PyYAML is not installed (pip install pyyaml), or write it as .json")
            items = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        elif path.suffix == ".json" and path.name != SEEN.name:
            items = json.loads(path.read_text(encoding="utf-8"))
        else:
            continue
        for o in items:
            o["_file"] = path.stem
            out.append(o)
    return out


def seen() -> dict:
    return json.loads(SEEN.read_text(encoding="utf-8")) if SEEN.is_file() else {}


# ------------------------------------------------------------------ plan: is every slot filled?

def plan(orders: list[dict]) -> int:
    problems, ids = [], {}
    for o in orders:
        oid = o.get("id", f"<no id in {o['_file']}>")
        if oid in ids:
            problems.append(f"{oid}: id used twice")
        ids[oid] = o
        for slot in SLOTS + (FAULT_SLOTS if o.get("kind") == "fault" else ()):
            if o.get(slot) in (None, "", []) and not (slot == "needs" and o.get(slot) == []):
                problems.append(f"{oid}: slot `{slot}` is empty")
        if o.get("kind") not in ("build", "fault"):
            problems.append(f"{oid}: kind must be build or fault")
        if len(o.get("if_it_fails") or []) < 2:
            problems.append(f"{oid}: if_it_fails needs at least two lines: what is seen, then what is DONE")
        t = o.get("test") or {}
        if t.get("type") not in TESTS:
            problems.append(f"{oid}: test type {t.get('type')!r} is not one of {', '.join(TESTS)}")
        else:
            for key in TESTS[t["type"]]:
                if key not in t:
                    problems.append(f"{oid}: a {t['type']} test needs `{key}`")
        for slot in ("from", "kept", "shown"):
            for m in re.finditer(r"`([^`]+)`(\s*\(new\))?", str(o.get(slot) or "")):
                p = m.group(1).split(",")[0].strip()
                if "/" in p and not m.group(2) and not (ROOT / p).exists():
                    problems.append(f"{oid}: {slot} names `{p}`, which is not in the repository (write (new) after a file the order creates)")
    for o in orders:
        for need in o.get("needs") or []:
            if need not in ids:
                problems.append(f"{o.get('id')}: needs {need}, which is no order")
    for p in problems:
        print(p)
    print(f"plan: {len(orders)} orders, {len(problems)} gap(s)")
    return 1 if problems else 0


# ------------------------------------------------------------------ the tests

def get_page(site: str, page: str) -> tuple[int, bytes]:
    if site.startswith("http"):
        url = site.rstrip("/") + "/" + page.lstrip("/")
        req = urllib.request.Request(url, headers={"User-Agent": "own-site-orders-check"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, b""
    path = Path(site) / (page.lstrip("/") or "index.html")
    if path.is_dir():
        path = path / "index.html"
    return (200, path.read_bytes()) if path.is_file() else (404, b"")


def select(node, selector: str) -> list:
    if selector.startswith(("/", "./", "(")):
        return node.xpath(selector)
    try:
        return node.cssselect(selector)
    except ImportError as e:  # lxml without cssselect
        raise RuntimeError("a CSS selector needs the cssselect package (pip install cssselect), or write it as XPath") from e


def visible_text(html: bytes) -> str:
    from lxml import html as lhtml
    doc = lhtml.fromstring(html or b"<html/>")
    for bad in doc.xpath("//script|//style|//head"):
        bad.drop_tree()
    return " ".join(doc.text_content().split())


def run_test(t: dict, site: str) -> tuple[bool, str]:
    kind = t["type"]
    if kind == "command":
        r = subprocess.run(t["run"], shell=True, cwd=ROOT, capture_output=True, text=True, timeout=t.get("timeout", 600))
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
        return r.returncode == 0, f"exit {r.returncode}: {tail[0][:160]}"
    if kind == "person":
        proof = str(t["proof"])
        if proof.startswith("words:"):
            words = proof[6:].strip()
            owner = (ROOT / "OWNER_WORDS.md").read_text(encoding="utf-8") if (ROOT / "OWNER_WORDS.md").is_file() else ""
            return words in owner, "the owner's words are in OWNER_WORDS.md" if words in owner else "waiting on the owner"
        return (ROOT / proof).is_file(), f"proof file {proof} {'exists' if (ROOT / proof).is_file() else 'is not there yet'}"
    pages = t.get("pages") or [t.get("page", "/")]
    details, ok_all = [], True
    for page in pages:
        status, body = get_page(site, page)
        if kind == "answers":
            ok, d = status == 200, f"{page} answered {status}"
        elif status != 200:
            ok, d = False, f"{page} answered {status}"
        elif kind == "bytes":
            ok, d = len(body) <= t["at_most"], f"{page} is {len(body)} bytes (at most {t['at_most']})"
        elif kind == "text":
            text = visible_text(body)
            missing = [p for p in t.get("has", []) if not re.search(p, text, re.I)]
            present = [p for p in t.get("lacks", []) if re.search(p, text, re.I)]
            ok, d = not missing and not present, f"{page}: missing {missing or 'nothing'}, should not say {present or 'nothing'}"
        else:
            from lxml import html as lhtml
            doc = lhtml.fromstring(body)
            if kind == "count":
                n = len(select(doc, t.get("css") or t.get("xpath")))
                ok = n >= t.get("at_least", 0) and n <= t.get("at_most", 10**9) and ("exactly" not in t or n == t["exactly"])
                d = f"{page}: {n} found"
            else:  # share
                rows = select(doc, t["of"])
                hits = sum(1 for r in rows if select(r, t["with"]))
                share = hits / len(rows) if rows else 0.0
                ok, d = bool(rows) and share >= t.get("at_least", 0.99), f"{page}: {hits} of {len(rows)} rows ({share:.0%}, at least {t.get('at_least', 0.99):.0%})"
        ok_all = ok_all and ok
        details.append(d)
    return ok_all, "; ".join(details)


def pick(orders: list[dict], names: list[str]) -> list[dict]:
    if not names:
        return orders
    if names == ["faults"]:
        return [o for o in orders if is_open(o, seen())]
    return [o for o in orders if o.get("id") in names or o["_file"] in names]


def run(orders: list[dict], names: list[str], site: str, record: bool) -> int:
    live = site.rstrip("/") == (CONF.get("live_url") or "").rstrip("/")
    if record and not live:
        sys.exit("orders: --record writes only what the LIVE product showed; drop --site or --record")
    book, now, failed = seen(), dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), 0
    for o in pick(orders, names):
        try:
            ok, detail = run_test(o["test"], site)
        except Exception as e:  # noqa: BLE001 — a broken test is a result, and never a pass
            ok, detail = False, f"the test itself broke: {type(e).__name__}: {e}"
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {o['id']:<14} {detail}")
        if record:
            before = book.get(o["id"], {})
            book[o["id"]] = {"pass": ok, "at": now, "site": site, "detail": detail[:300],
                             "ever_passed": bool(before.get("ever_passed")) or ok}
    if record:
        SEEN.write_text(json.dumps(book, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"run: {failed} failing" + (" (recorded)" if record else ""))
    return 1 if failed else 0


# ------------------------------------------------------------------ faults and the count

def is_open(o: dict, book: dict) -> bool:
    s = book.get(o.get("id"), {})
    if o.get("kind") == "fault":
        return not s.get("pass")
    return bool(s.get("ever_passed")) and not s.get("pass")  # passed once and fails now: a fault again


def faults(orders: list[dict]) -> int:
    book = seen()
    open_ = sorted((o for o in orders if is_open(o, book)), key=lambda o: str(o.get("found") or "0"))
    fixed = [o for o in orders if o.get("kind") == "fault" and book.get(o["id"], {}).get("pass")]
    for o in open_:
        print(f"  {o['id']}: {o.get('what')}\n     found {o.get('found', 'earlier (passed once, fails now)')} · "
              f"next: {o.get('next', 'see its if_it_fails')}")
    print(f"faults: {len(open_)} open, {len(fixed)} fixed and seen fixed on the live product")
    return 1 if open_ else 0


def tally(orders: list[dict]) -> int:
    book, files = seen(), {}
    for o in orders:
        f = files.setdefault(o["_file"], [0, 0])
        f[1] += 1
        f[0] += bool(book.get(o["id"], {}).get("pass"))
    for name, (p, n) in sorted(files.items()):
        print(f"  {name:<16} {p} of {n} passing")
    total = sum(n for _, n in files.values())
    print(f"count: {sum(p for p, _ in files.values())} of {total} orders pass on the live product"
          f" ({sum(1 for p, n in files.values() if p == n)} of {len(files)} files complete)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["plan", "run", "faults", "count"])
    ap.add_argument("names", nargs="*")
    ap.add_argument("--site", default=CONF.get("live_url") or "")
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()
    orders = load_orders()
    if a.command == "plan":
        return plan(orders)
    if a.command == "run":
        return run(orders, a.names, a.site, a.record)
    if a.command == "faults":
        return faults(orders)
    return tally(orders)


if __name__ == "__main__":
    sys.exit(main())
