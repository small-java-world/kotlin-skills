#!/usr/bin/env python3
"""Run fixture-based tests for skill_output_lint.py."""

from __future__ import annotations

import pathlib
import subprocess
import sys


def main() -> int:
    script_dir = pathlib.Path(__file__).resolve().parent
    root = script_dir.parent
    lint_script = script_dir / "skill_output_lint.py"
    fixture_dir = root / "tests" / "fixtures"

    expected = {
        "good_01.json": 0,
        "good_02.json": 0,
        "good_03.md": 0,
        "bad_01_missing_evidence.json": 2,
        "bad_02_missing_severity.md": 2,
        "bad_03_ambiguous_duplicate.json": 1,
        "bad_04_position_duplicate.json": 1,
    }

    failed: list[str] = []
    for filename, expected_code in expected.items():
        path = fixture_dir / filename
        proc = subprocess.run(
            [sys.executable, str(lint_script), "--input", str(path), "--profile", "clean-code"],
            capture_output=True,
            text=True,
            check=False,
        )
        ok = proc.returncode == expected_code
        status = "PASS" if ok else "FAIL"
        print(f"{status} {filename}: expected={expected_code}, actual={proc.returncode}")
        if not ok:
            failed.append(filename)
            if proc.stdout.strip():
                print(proc.stdout.strip())
            if proc.stderr.strip():
                print(proc.stderr.strip())

    if failed:
        print("Failed fixtures:", ", ".join(failed))
        return 1

    print("All fixture tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

