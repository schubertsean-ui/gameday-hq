#!/usr/bin/env python3
"""spend — the month's money against the owner's cap (kit.json "monthly_cap_usd", all AI providers and paid services).

  python3 tools/spend.py status                     this month: spent, cap, share. Exit 0 under the cap (a WARN line
                                                    from kit.json "spend_warn_at", default 80%), 2 at or over the cap
  python3 tools/spend.py before --provider P --what "W" --estimate E
                                                    BEFORE any paid run: refuses (exit 2, nothing logged) when the
                                                    month plus E would reach the cap; else logs the run, prints its id
  python3 tools/spend.py after ID --actual A        AFTER the run: the real cost, read from the provider where it can be

The month's figure is the larger of two sums: the ledger (docs/SPEND_LEDGER.yaml; a run with no actual yet counts at
its estimate) and the bills copied from each provider (docs/SPEND.yaml; a bill marked counts_toward_cap: false, such as
a flat plan the owner pays outside the cap, is shown there but not counted). This is the AI's own brake. The hard backstop
is the cap the owner sets on each provider's billing page; this tool cannot stop a provider charging.
Exit 3: the ledger or the bills could not be read (never a pass).
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from kitconf import CONF  # noqa: E402

LEDGER = ROOT / CONF["spend"]["ledger"]
BILLS = ROOT / CONF["spend"]["bills"]


def _load_list(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if isinstance(data, dict):
        data = data.get("entries") or []
    if not isinstance(data, list):
        raise ValueError(f"{path.name} is not a list of entries")
    return data


def _money(v) -> float:
    return float(str(v).replace("$", "").replace(",", "")) if v not in (None, "") else 0.0


def month_total(ledger: list[dict], bills: list[dict], month: str) -> tuple[float, float, float]:
    """(the figure used, the ledger's sum, the bills' sum) for one month, YYYY-MM."""
    led = sum(_money(e.get("actual_usd") if e.get("actual_usd") not in (None, "") else e.get("estimate_usd"))
              for e in ledger if str(e.get("date", ""))[:7] == month)
    bil = sum(_money(b.get("amount")) for b in bills
              if str(b.get("month", "")) == month and b.get("counts_toward_cap", True) is not False)
    return max(led, bil), led, bil


def verdict(total: float, cap: float, warn_at: float) -> tuple[int, str]:
    share = total / cap if cap else 1.0
    line = f"${total:,.2f} of ${cap:,.2f} this month ({share:.0%})"
    if total >= cap:
        return 2, f"STOP: {line} — at the cap. Paid work halts; unpaid work goes on. More needs the owner's yes."
    if share >= warn_at:
        return 0, f"WARN: {line} — past {warn_at:.0%} of the cap; say so in the morning summary."
    return 0, f"ok: {line}"


def _write(entries: list[dict]) -> None:
    head = []
    if LEDGER.is_file():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.startswith("#"):
                break
            head.append(line)
    body = yaml.safe_dump(entries, sort_keys=False, allow_unicode=True) if entries else "[]\n"
    LEDGER.write_text("\n".join(head) + ("\n" if head else "") + body, encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="the month's spend against the cap")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    b = sub.add_parser("before")
    b.add_argument("--provider", required=True)
    b.add_argument("--what", required=True)
    b.add_argument("--estimate", required=True, type=float)
    a = sub.add_parser("after")
    a.add_argument("id")
    a.add_argument("--actual", required=True, type=float)
    ap.add_argument("--month", default=dt.date.today().strftime("%Y-%m"))
    args = ap.parse_args(argv)
    cap, warn_at = float(CONF["monthly_cap_usd"]), float(CONF.get("spend_warn_at", 0.8))
    try:
        ledger, bills = _load_list(LEDGER), _load_list(BILLS)
    except (ValueError, yaml.YAMLError) as e:
        print(f"spend: could not read the ledger or the bills ({e}) — NOT RUN")
        return 3
    total, led, bil = month_total(ledger, bills, args.month)
    if args.cmd in (None, "status"):
        code, line = verdict(total, cap, warn_at)
        print(f"spend {args.month}: {line}  [ledger ${led:,.2f} · bills ${bil:,.2f}]")
        return code
    if args.cmd == "before":
        if args.estimate < 0:
            print("spend: an estimate cannot be negative")
            return 2
        code, line = verdict(total + args.estimate, cap, warn_at)
        if code:
            print(f"spend: REFUSED — this run (${args.estimate:,.2f}) would take the month to {line}")
            return 2
        new_id = f"{dt.date.today():%Y%m%d}-{len(ledger) + 1:03d}"
        ledger.append({"id": new_id, "date": dt.date.today().isoformat(), "provider": args.provider, "what": args.what,
                       "estimate_usd": round(args.estimate, 2), "actual_usd": None})
        _write(ledger)
        print(f"spend: logged {new_id} — after this run the month is at most {line}")
        return 0
    for e in ledger:
        if str(e.get("id")) == args.id:
            e["actual_usd"] = round(args.actual, 2)
            _write(ledger)
            total, _, _ = month_total(ledger, bills, args.month)
            code, line = verdict(total, cap, warn_at)
            print(f"spend: {args.id} actual ${args.actual:,.2f}; {line}")
            return code
    print(f"spend: no ledger entry {args.id}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
