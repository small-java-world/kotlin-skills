#!/usr/bin/env python3
"""PreToolUse hook: block destructive Bash commands in agent context.

Reads tool input JSON from stdin (Claude Code hook protocol).
Exit 0 = allow, exit 2 = block (stdout is shown to model as error).
"""

import json
import re
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Patterns that indicate destructive operations
BLOCKED_PATTERNS = [
    # File deletion / overwrite
    r"\brm\s+.*-[rf]",
    r"\brm\s+-[rf]",
    r"\brmdir\b",
    r"\btruncate\b",
    # Dangerous redirects (overwrite) — block both absolute and relative paths
    r"(?<!>)>\s*[^>&\s/]",          # single > to relative path (e.g. > file); allows >> (append)
    r">\s*/(?!dev/null)",          # redirect to absolute path (allow /dev/null)
    r"\btee\b(?!.*--append)",      # tee without --append overwrites (NOTE: lookahead scans full string; edge case with chained commands)
    # Git destructive ops
    r"\bgit\s+push\s+.*(?:--force(?:-with-lease)?|-f\b)",
    r"\bgit\s+reset\s+--hard",
    r"\bgit\s+clean\s+-[fd]",
    r"\bgit\s+checkout\s+(?:-f\b|--force\b)",
    r"\bgit\s+branch\s+-[Dd]",
    # Permission / ownership changes
    r"\bchmod\b",
    r"\bchown\b",
    # Process termination
    r"\bkill\b",
    r"\bpkill\b",
    r"\bkillall\b",
    # Disk / format operations
    r"\bdd\s+",
    r"\bmkfs\b",
    r"\bfdisk\b",
    # Fork bomb
    r":\(\)\s*\{",
    # Package installation (agents should not install)
    r"\bpip\s+install\b",
    r"\bnpm\s+install\b",
    r"\bapt\s+install\b",
]

BLOCKED_RE = re.compile("|".join(BLOCKED_PATTERNS), re.IGNORECASE)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as exc:
        # Fail-closed: block when input cannot be parsed (security principle)
        print(
            f"[validate-bash hook] BLOCKED: stdin JSON パースエラー ({exc.__class__.__name__})。\n"
            f"  安全側に倒すためコマンドをブロックします。",
            file=sys.stderr,
        )
        return 2

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        return 0

    match = BLOCKED_RE.search(command)
    if match:
        print(
            f"[validate-bash hook] BLOCKED: 破壊的なコマンドはエージェントコンテキストでは使用できません。\n"
            f"  コマンド: {command[:120]}\n"
            f"  マッチパターン: {match.group()}\n"
            f"  許可されるコマンド: grep/find/cat/ls などの読み取り専用コマンドと ./gradlew test のみ。",
            file=sys.stderr,
        )
        return 2  # block

    return 0  # allow


if __name__ == "__main__":
    sys.exit(main())
