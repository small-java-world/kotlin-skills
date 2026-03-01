#!/usr/bin/env python3
"""Run Kotlin evaluation pipeline with optional self-test mode."""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Kotlin eval tests.")
    parser.add_argument(
        "--root",
        default=str(pathlib.Path(__file__).resolve().parent.parent / "tests" / "kotlin_eval"),
        help="kotlin_eval root directory",
    )
    parser.add_argument(
        "--actual-dir",
        default="",
        help="directory containing model outputs named <case_id>.json or .md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="use expected findings as mock actual outputs",
    )
    return parser.parse_args()


def build_manifest(script_dir: pathlib.Path, root: pathlib.Path) -> pathlib.Path:
    manifest = root / "kotlin_eval_manifest.json"
    proc = subprocess.run(
        [sys.executable, str(script_dir / "build_kotlin_eval_manifest.py"), "--root", str(root), "--out", str(manifest)],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit("failed to build manifest")
    return manifest


def prepare_self_test_actual(manifest_path: pathlib.Path) -> pathlib.Path:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    tmp_dir = pathlib.Path(tempfile.mkdtemp(prefix="kotlin_eval_actual_"))
    for case in data.get("cases", []):
        case_id = case["case_id"]
        expected = manifest_path.parent / case["expected_file"]
        shutil.copyfile(expected, tmp_dir / f"{case_id}.json")
    return tmp_dir


def main() -> int:
    args = parse_args()
    script_dir = pathlib.Path(__file__).resolve().parent
    root = pathlib.Path(args.root)

    manifest = build_manifest(script_dir, root)
    if args.self_test:
        actual_dir = prepare_self_test_actual(manifest)
        cleanup = True
    elif args.actual_dir:
        actual_dir = pathlib.Path(args.actual_dir)
        cleanup = False
    else:
        raise SystemExit("provide --actual-dir or use --self-test")

    report_path = root / "score_report.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(script_dir / "score_kotlin_eval.py"),
            "--manifest",
            str(manifest),
            "--actual-dir",
            str(actual_dir),
            "--out",
            str(report_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    print(proc.stdout.strip())
    if proc.returncode != 0:
        print(proc.stderr.strip())
        return proc.returncode

    report = json.loads(report_path.read_text(encoding="utf-8"))
    score = report["score"]["total"]
    grade = report["score"]["grade"]
    print(f"score: {score} ({grade})")
    print(f"report: {report_path}")

    if cleanup:
        shutil.rmtree(actual_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

