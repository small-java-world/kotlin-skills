#!/usr/bin/env python3
"""Build manifest for Kotlin evaluation corpus."""

from __future__ import annotations

import argparse
import json
import pathlib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build kotlin evaluation manifest.")
    parser.add_argument(
        "--root",
        default=str(pathlib.Path(__file__).resolve().parent.parent / "tests" / "kotlin_eval"),
        help="kotlin_eval root directory",
    )
    parser.add_argument(
        "--out",
        default="",
        help="output manifest path (default: <root>/kotlin_eval_manifest.json)",
    )
    return parser.parse_args()


def parse_context_metadata(context_path: pathlib.Path) -> dict[str, str]:
    data = {
        "case_id": "",
        "category": "",
        "difficulty": "",
        "source_refs": "",
    }
    for line in context_path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        k = key.strip().lower().replace(" ", "_")
        if k in data:
            data[k] = value.strip()
        if all(data.values()):
            break
    return data


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.root)
    cases_dir = root / "cases"
    if not cases_dir.exists():
        raise SystemExit(f"cases directory not found: {cases_dir}")

    manifest_path = pathlib.Path(args.out) if args.out else root / "kotlin_eval_manifest.json"
    cases: list[dict[str, object]] = []

    for case_dir in sorted([d for d in cases_dir.iterdir() if d.is_dir()]):
        input_file = case_dir / "input_bad.kt"
        context_file = case_dir / "context.md"
        expected_file = case_dir / "expected_findings.json"
        if not (input_file.exists() and context_file.exists() and expected_file.exists()):
            continue

        meta = parse_context_metadata(context_file)
        case_id = meta["case_id"] or case_dir.name
        source_refs = [s.strip() for s in meta["source_refs"].split(",") if s.strip()]
        cases.append(
            {
                "case_id": case_id,
                "category": meta["category"] or "unknown",
                "difficulty": meta["difficulty"] or "unknown",
                "input_file": str(input_file.relative_to(root)).replace("\\", "/"),
                "context_file": str(context_file.relative_to(root)).replace("\\", "/"),
                "expected_file": str(expected_file.relative_to(root)).replace("\\", "/"),
                "source_refs": source_refs,
            }
        )

    manifest = {
        "version": "1.0",
        "domain": "kotlin-web-backend",
        "case_count": len(cases),
        "cases": cases,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written: {manifest_path}")
    print(f"cases: {len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

