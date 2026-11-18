"""The two lanes, the test floor and the spending cap, held as tests (kit 1.1.1).

  - a change touching a red-lane path, an existing test, a lowered floor or a new paid app is RED: the AI never merges it
  - an ordinary product change under the size limit is GREEN; a bigger one is NOT YET (split it)
  - the AI's own merge also needs the required check green and a review by a different model at the head commit
  - every red-lane path is owned by the owner in CODEOWNERS, so the code host holds the line too
  - the month's spend stops paid work at the cap and warns at 80%
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "checks"))
import floor  # noqa: E402
import lane  # noqa: E402
import spend  # noqa: E402

KIT = json.loads((ROOT / "kit.json").read_text(encoding="utf-8"))


def _classify(changes, base=None, head=None, lines=10):
    base, head = base or {}, head or {}
    return lane.classify(changes, base.get, head.get, lines, lane.CONF, lambda p: True)


def test_glob_patterns():
    assert lane.glob_match(".github/**", ".github/workflows/checks.yml")
    assert lane.glob_match("**/migrations/**", "db/migrations/0001.sql")
    assert lane.glob_match("**/migrations/**", "migrations/0001.sql")
    assert lane.glob_match("**/.env*", "app/.env.production")
    assert lane.glob_match("*.lock", "deep/Cargo.lock")
    assert not lane.glob_match("tools/check", "tools/checks/check.py")
    assert not lane.glob_match(".github/**", "src/github.js")


def test_an_ordinary_product_change_is_green():
    code, why = _classify([("M", "src/App.js", "src/App.js"), ("A", "tests/test_new.py", "tests/test_new.py")])
    assert code == lane.GREEN, why


def test_red_lane_paths_are_flagged():
    for path in [".github/workflows/checks.yml", "tools/checks/check.py", "tools/check", "tools/hooks/protect_tests.py",
                 ".claude/settings.json", "kit.json", "AGENTS.md", "db/migrations/0002_add.sql", ".env", "vercel.json",
                 "supabase/functions/x.ts", "prisma/schema.prisma", "db/seeds/users.js", "src/stripe/client.js",
                 "src/components/StripeCheckout.jsx", "src/billing/invoice.js", "api/payments/charge.js",
                 "config/pricing.json", "src/checkout/Cart.jsx"]:
        code, why = _classify([("M", "src/App.js", "src/App.js"), ("M", path, path)])
        assert code == lane.RED and any(path in w for w in why), (path, why)


def test_the_site_itself_is_green_so_it_publishes_after_checks():
    for path in ["src/App.js", "src/index.js", "public/index.html", "src/components/Header.jsx", "README.md"]:
        assert _classify([("M", path, path)])[0] == lane.GREEN, path


def test_changing_or_deleting_an_existing_test_is_red():
    for status in "MD":
        code, why = _classify([(status, "tests/test_ops.py", "tests/test_ops.py")])
        assert code == lane.RED, why


def test_the_floor_may_go_up_but_never_down_in_the_green_lane():
    f = "tools/checks/test_floor.txt"
    assert _classify([("M", f, f)], {f: "24\n"}, {f: "30\n"})[0] == lane.GREEN
    code, why = _classify([("M", f, f)], {f: "24\n"}, {f: "20\n"})
    assert code == lane.RED and "floor goes down" in " ".join(why)


def test_a_new_paid_app_is_red_and_a_review_date_is_green():
    a = "docs/APPS.yaml"
    base = {a: "- name: GitHub\n  plan: Team\n  cap: $5\n  next_review: 2026-12-18\n"}
    dated = {a: "- name: GitHub\n  plan: Team\n  cap: $5\n  next_review: 2027-01-18\n"}
    added = {a: base[a] + "- name: NewThing\n  plan: Pro\n  cap: $20\n"}
    recapped = {a: "- name: GitHub\n  plan: Team\n  cap: $50\n"}
    assert _classify([("M", a, a)], base, dated)[0] == lane.GREEN
    assert _classify([("M", a, a)], base, added)[0] == lane.RED
    assert _classify([("M", a, a)], base, recapped)[0] == lane.RED


def test_a_change_over_the_size_limit_waits_to_be_split():
    limit = KIT["auto_merge"]["max_changed_lines"]
    assert _classify([("M", "src/App.js", "src/App.js")], lines=limit)[0] == lane.GREEN
    assert _classify([("M", "src/App.js", "src/App.js")], lines=limit + 1)[0] == lane.NOT_YET


def test_the_merge_needs_a_review_by_another_model_at_the_head_commit():
    sha, body = "abc1234def5678", "What it does.\nbuilder-model: claude-sonnet-5.5\n"
    good = [{"body": "REVIEW: PASS abc1234\nreviewer-model: gpt-6.2-astra\nRead the whole diff."}]
    assert lane.review_passed(good, sha, body)[0]
    assert not lane.review_passed([{"body": "REVIEW: PASS abc1234\nreviewer-model: claude-sonnet-5.5"}], sha, body)[0]
    assert not lane.review_passed([{"body": "REVIEW: PASS 9999999\nreviewer-model: gpt-6.2-astra"}], sha, body)[0]
    assert not lane.review_passed(good, sha, "no builder named")[0]


def test_the_merge_needs_the_required_check_green():
    assert lane.checks_green([{"name": "checks", "conclusion": "SUCCESS"}], "checks")[0]
    assert not lane.checks_green([{"name": "checks", "conclusion": "FAILURE"}], "checks")[0]
    assert not lane.checks_green([{"name": "checks", "conclusion": ""}], "checks")[0]
    assert not lane.checks_green([], "checks")[0]


def _codeowners_pattern(p: str) -> str:
    """kit.json's red-lane glob, written the way CODEOWNERS (gitignore rules) writes it."""
    anywhere = p.startswith("**/")
    p = p[3:] if anywhere else p
    p = p[:-2] if p.endswith("/**") else p
    if anywhere or ("/" not in p.rstrip("/") and p.startswith("*")):
        return p if "/" not in p.rstrip("/") else "**/" + p
    return "/" + p


def test_every_red_lane_path_is_owned_in_codeowners():
    owner = "@" + KIT["owner_github"]
    owned = {}
    for ln in (ROOT / ".github" / "CODEOWNERS").read_text().splitlines():
        if ln.strip() and not ln.startswith("#"):
            parts = ln.split()
            owned[parts[0]] = parts[1:]
    for p in KIT["red_lane"]["paths"]:
        pat = _codeowners_pattern(p)
        assert owner in owned.get(pat, []), f"{p} is red lane but CODEOWNERS has no '{pat} {owner}' line"
    assert owned.get("/tools/checks/test_floor.txt") == [], "raising the floor must stay green (no owner on that line)"


def test_the_cap_and_the_roles_are_set():
    assert KIT["monthly_cap_usd"] > 0 and 0 < KIT["spend_warn_at"] < 1
    roles = KIT["roles"]
    for r in ("coordinator", "builder", "reviewer", "reader", "scout"):
        assert roles[r]["model"] and roles[r]["vendor"], r
    assert roles["reviewer"]["model"] != roles["builder"]["model"], "the reviewer must not be the builder's model"


def test_spend_warns_at_80_percent_and_stops_at_the_cap():
    assert spend.verdict(39.99, 50, 0.8)[0] == 0 and spend.verdict(39.99, 50, 0.8)[1].startswith("ok")
    assert spend.verdict(40, 50, 0.8)[0] == 0 and spend.verdict(40, 50, 0.8)[1].startswith("WARN")
    assert spend.verdict(50, 50, 0.8)[0] == 2
    ledger = [{"date": "2026-11-02", "estimate_usd": 5, "actual_usd": 3.5}, {"date": "2026-11-03", "estimate_usd": 2},
              {"date": "2026-10-30", "estimate_usd": 99}]
    bills = [{"month": "2026-11", "amount": 4}, {"month": "2026-11", "amount": 200, "counts_toward_cap": False}]
    assert spend.month_total(ledger, bills, "2026-11") == (5.5, 5.5, 4.0)


def test_spend_before_refuses_over_the_cap_and_after_records_the_actual(tmp_path, monkeypatch, capsys):
    led = tmp_path / "SPEND_LEDGER.yaml"
    led.write_text("# header\n[]\n")
    monkeypatch.setattr(spend, "LEDGER", led)
    monkeypatch.setattr(spend, "BILLS", tmp_path / "none.yaml")
    month = __import__("datetime").date.today().strftime("%Y-%m")
    cap = float(KIT["monthly_cap_usd"])
    assert spend.main(["before", "--provider", "X", "--what", "a run", "--estimate", str(cap - 1)]) == 0
    entry = spend._load_list(led)[0]
    assert led.read_text().startswith("# header") and entry["actual_usd"] is None
    assert spend.main(["before", "--provider", "X", "--what", "too much", "--estimate", "1"]) == 2
    assert len(spend._load_list(led)) == 1, "a refused run is not logged"
    assert spend.main(["after", entry["id"], "--actual", str(cap + 5)]) == 2
    assert spend.main(["--month", month, "status"]) == 2


def test_the_floor_reads_and_counts(tmp_path):
    assert floor.read_floor("24\n") == 24 and floor.read_floor("") == 0
    assert floor.parse_collected("x\n24 tests collected in 0.05s\n") == 24
    assert floor.parse_collected("22 tests collected, 1 error in 0.1s") is None
    (tmp_path / "test_a.py").write_text("def test_one():\n    pass\nclass TestB:\n    def test_two(self):\n        pass\ndef helper():\n    pass\n")
    assert floor.static_count(tmp_path) == 2


def test_every_pip_cache_names_the_kit_requirements():
    """setup-python's pip cache fails the job when no requirements.txt exists (gameday-hq's first check, 18 Nov 2026)."""
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        for line in wf.read_text(encoding="utf-8").splitlines():
            if "cache: pip" in line:
                assert "cache-dependency-path:" in line, f"{wf.name}: 'cache: pip' without cache-dependency-path"
