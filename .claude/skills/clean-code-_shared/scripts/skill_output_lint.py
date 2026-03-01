#!/usr/bin/env python3
"""Lint clean-code skill outputs.

Exit codes:
0: pass
1: warnings only
2: errors
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass
from typing import Iterable

SEVERITIES = {"critical", "high", "medium", "low"}
AMBIGUOUS_TERMS = {
    "somehow",
    "maybe",
    "possibly",
    "as needed",
    "適宜",
    "なんとなく",
    "たぶん",
    "いい感じ",
}
# L1: Valid rule_id pattern
RULE_ID_PATTERN = re.compile(r"^CC-[PCT]\d{3}$")

# F4: Exhaustive allowlist of defined rules (15 rules)
VALID_RULE_IDS = {
    "CC-P001", "CC-P002", "CC-P003", "CC-P004", "CC-P005", "CC-P006",
    "CC-C001", "CC-C002", "CC-C003", "CC-C004",
    "CC-T001", "CC-T002", "CC-T003", "CC-T004", "CC-T005",
}

# L5: ACTION_WORDS for verification executability check (word-boundary safe via \b)
ACTION_WORDS_PATTERN = re.compile(
    r"\b(?:add|extract|split|remove|introduce|replace|rename|run|assert|test|verify|"
    r"追加|抽出|分離|削除|置換|実行|検証|確認)\b",
    re.IGNORECASE,
)


@dataclass
class Finding:
    severity: str
    rule_id: str
    evidence: str
    minimal_fix: str
    verification: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint clean-code skill outputs.")
    parser.add_argument("--input", required=True, help="Path to output file (.json or .md/.txt)")
    parser.add_argument("--profile", default="clean-code", help="Lint profile; must be clean-code")
    parser.add_argument(
        "--allow-empty-findings",
        action="store_true",
        default=False,
        help="Treat empty findings[] as valid (for false-positive-resilience cases)",
    )
    return parser.parse_args()


def load_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_json_findings(text: str) -> list[Finding]:
    data = json.loads(text)
    findings = data.get("findings")
    if not isinstance(findings, list):
        raise ValueError("JSON must contain findings[]")
    parsed: list[Finding] = []
    for idx, item in enumerate(findings, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"findings[{idx}] must be an object")
        parsed.append(
            Finding(
                severity=str(item.get("severity", "")).strip(),
                rule_id=str(item.get("rule_id", "")).strip(),
                evidence=str(item.get("evidence", "")).strip(),
                minimal_fix=str(item.get("minimal_fix", "")).strip(),
                verification=str(item.get("verification", "")).strip(),
            )
        )
    return parsed


def _extract_field(block: str, label: str) -> str:
    """Extract a field value that may span multiple lines.

    L4: Reads from the label until the next field label or end of block.
    """
    # Match the label line
    label_pattern = re.compile(rf"(?im)^\s*{re.escape(label)}\s*:\s*(.*)$")
    match = label_pattern.search(block)
    if not match:
        return ""

    first_line = match.group(1).strip()
    rest_start = match.end()
    rest_text = block[rest_start:]

    # Known field labels — stop collecting when another one is encountered
    field_labels = (
        "Severity",
        "Rule_ID",
        "RuleID",
        "Evidence",
        "Minimal_Fix",
        "Minimal Fix",
        "Verification",
    )
    stop_pattern = re.compile(
        r"(?im)^\s*(?:" + "|".join(re.escape(fl) for fl in field_labels) + r")\s*:"
    )
    stop_match = stop_pattern.search(rest_text)
    continuation = rest_text[: stop_match.start()] if stop_match else rest_text

    extra_lines = [ln.strip() for ln in continuation.splitlines() if ln.strip()]
    parts = [first_line] + extra_lines
    return " ".join(parts).strip()


def _find_findings_section(text: str) -> str:
    """L3: Restrict finding extraction to the ## Findings section."""
    # Accept both '## Findings' and '## Finding' headers
    header_pattern = re.compile(r"(?im)^##\s+Findings?\s*$")
    match = header_pattern.search(text)
    if match:
        # Take text from the header to the next ## section (or end)
        next_section = re.compile(r"(?im)^##\s+")
        following = next_section.search(text, match.end())
        return text[match.end() : following.start()] if following else text[match.end():]
    # If no header found, fall back to entire text (lenient mode)
    return text


def parse_markdown_findings(text: str) -> list[Finding]:
    # L3: Restrict to ## Findings section
    section = _find_findings_section(text)

    pattern = re.compile(r"(?m)^\s*\d+\.\s+")
    matches = list(pattern.finditer(section))
    if not matches:
        # Allow empty findings section (validated later by lint_findings)
        return []

    blocks: list[str] = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(section)
        blocks.append(section[start:end].strip())

    parsed: list[Finding] = []
    for block in blocks:
        parsed.append(
            Finding(
                severity=_extract_field(block, "Severity"),
                rule_id=_extract_field(block, "Rule_ID") or _extract_field(block, "RuleID"),
                evidence=_extract_field(block, "Evidence"),
                minimal_fix=_extract_field(block, "Minimal_Fix") or _extract_field(block, "Minimal Fix"),
                verification=_extract_field(block, "Verification"),
            )
        )
    return parsed


def parse_findings(path: pathlib.Path, text: str) -> list[Finding]:
    if path.suffix.lower() == ".json":
        return parse_json_findings(text)
    return parse_markdown_findings(text)


def contains_ambiguous_terms(values: Iterable[str]) -> list[str]:
    hits: list[str] = []
    joined = " ".join(values).lower()
    for term in AMBIGUOUS_TERMS:
        if term.lower() in joined:
            hits.append(term)
    return sorted(set(hits))


def lint_findings(
    findings: list[Finding], *, allow_empty: bool = False
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not findings:
        if allow_empty:
            return errors, warnings
        errors.append("No findings found.")
        return errors, warnings

    seen: set[tuple[str, str]] = set()
    for idx, f in enumerate(findings, start=1):
        prefix = f"finding[{idx}]"

        # Severity checks (L2: normalize case before checking)
        severity_normalized = f.severity.lower()
        if not f.severity:
            errors.append(f"{prefix}: missing severity")
        elif severity_normalized not in SEVERITIES:
            errors.append(f"{prefix}: invalid severity '{f.severity}'")

        # rule_id checks (L1: validate format, F4: validate against allowlist)
        if not f.rule_id:
            errors.append(f"{prefix}: missing rule_id")
        elif not RULE_ID_PATTERN.match(f.rule_id):
            errors.append(
                f"{prefix}: invalid rule_id format '{f.rule_id}' (expected CC-[PCT]NNN)"
            )
        elif f.rule_id not in VALID_RULE_IDS:
            errors.append(
                f"{prefix}: undefined rule_id '{f.rule_id}' "
                f"(valid: {', '.join(sorted(VALID_RULE_IDS))})"
            )

        if not f.evidence:
            errors.append(f"{prefix}: missing evidence")
        if not f.minimal_fix:
            errors.append(f"{prefix}: missing minimal_fix")
        if not f.verification:
            errors.append(f"{prefix}: missing verification")
        # L5: verification must contain an action word (executable check)
        elif not ACTION_WORDS_PATTERN.search(f.verification):
            warnings.append(
                f"{prefix}: verification lacks an action word - add a concrete command or assertion"
            )

        dup_key = (f.rule_id.lower(), re.sub(r"\s+", " ", f.evidence.lower()).strip())
        if dup_key in seen and all(dup_key):
            warnings.append(f"{prefix}: possible duplicate finding (rule_id + evidence)")
        else:
            seen.add(dup_key)

        amb = contains_ambiguous_terms(
            [f.evidence, f.minimal_fix, f.verification]
        )
        if amb:
            warnings.append(f"{prefix}: ambiguous terms found: {', '.join(amb)}")

    return errors, warnings


def main() -> int:
    args = parse_args()
    if args.profile != "clean-code":
        print(f"ERROR: unsupported profile '{args.profile}'. Use 'clean-code'.")
        return 2

    path = pathlib.Path(args.input)
    if not path.exists():
        print(f"ERROR: input not found: {path}")
        return 2

    try:
        text = load_text(path)
        findings = parse_findings(path, text)
        errors, warnings = lint_findings(findings, allow_empty=args.allow_empty_findings)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"ERROR: {exc}")
        return 2

    for err in errors:
        print(f"ERROR: {err}")
    for warn in warnings:
        print(f"WARN: {warn}")

    if errors:
        return 2
    if warnings:
        return 1
    print("OK: no issues found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
