#!/usr/bin/env bash
# tools/hooks/install_git_hooks.sh — the gate for ANY AI tool or person, not only Claude Code:
# git itself runs the product check before every commit (quick) and every push (full), and its exit code decides.
# Run once per copy of the repository: bash tools/hooks/install_git_hooks.sh
# A person can skip these with --no-verify; the code host's required check (.github/workflows/checks.yml) cannot be skipped.
set -eu
cd "$(dirname "$0")/../.."
hooks_dir="$(git rev-parse --git-path hooks)"
mkdir -p "$hooks_dir"
cat > "$hooks_dir/pre-commit" <<'EOF'
#!/usr/bin/env bash
# a red quick check stops the commit
exec bash tools/check --quick
EOF
cat > "$hooks_dir/pre-push" <<'EOF'
#!/usr/bin/env bash
# a red full check stops the push: nothing red leaves this copy
exec bash tools/check
EOF
chmod +x "$hooks_dir/pre-commit" "$hooks_dir/pre-push" tools/check tools/hooks/run tools/hooks/*.py tools/*.py 2>/dev/null || true
echo "installed pre-commit (quick check) and pre-push (full check) in $hooks_dir"
