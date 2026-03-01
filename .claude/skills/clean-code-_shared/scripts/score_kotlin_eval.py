#!/usr/bin/env python3
"""Score clean-code skill outputs against Kotlin evaluation corpus."""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass

# S2: Use word-boundary regex instead of substring matching
ACTION_WORDS_PATTERN = re.compile(
    r"\b(?:add|extract|split|remove|introduce|replace|rename|run|assert|test|verify|"
    r"追加|抽出|分離|削除|置換|実行|検証|確認)\b",
    re.IGNORECASE,
)


@dataclass
class ParsedFinding:
    severity: str
    rule_id: str
    evidence: str
    minimal_fix: str
    verification: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score Kotlin evaluation outputs.")
    parser.add_argument("--manifest", required=True, help="Path to kotlin_eval_manifest.json")
    parser.add_argument("--actual-dir", required=True, help="Directory containing <case_id>.json/.md outputs")
    parser.add_argument("--out", required=True, help="Path to write score report JSON")
    return parser.parse_args()


def load_lint_module(script_path: pathlib.Path):
    spec = importlib.util.spec_from_file_location("skill_output_lint", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load lint module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


def load_findings_via_lint(module, path: pathlib.Path) -> list[ParsedFinding]:
    text = path.read_text(encoding="utf-8")
    findings = module.parse_findings(path, text)
    return [
        ParsedFinding(
            severity=f.severity,
            rule_id=f.rule_id,
            evidence=f.evidence,
            minimal_fix=f.minimal_fix,
            verification=f.verification,
        )
        for f in findings
    ]


def safe_ratio(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def score_rule_f1(expected_rules: list[str], actual_rules: list[str]) -> tuple[float, dict]:
    """S1: Score rule matching using F1 (precision × recall harmonic mean).

    Prevents inflating scores by emitting many extra findings.
    """
    if not expected_rules:
        # No expected rules: penalise false positives but don't divide by zero
        precision = 1.0 if not actual_rules else 0.0
        return precision, {"precision": precision, "recall": 1.0, "f1": precision}

    # Use multiset matching so repeated rules in one case are scored correctly.
    expected_counts = collections.Counter(expected_rules)
    actual_counts = collections.Counter(actual_rules)

    tp = sum(min(expected_counts[rid], actual_counts[rid]) for rid in expected_counts)
    precision = safe_ratio(tp, len(actual_rules))
    recall = safe_ratio(tp, len(expected_rules))
    f1 = safe_ratio(2 * precision * recall, precision + recall)

    return f1, {"precision": round(precision, 3), "recall": round(recall, 3), "f1": round(f1, 3)}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def evidence_similarity(left: str, right: str) -> float:
    left_tokens = set(re.findall(r"[a-z0-9_]+", normalize_text(left)))
    right_tokens = set(re.findall(r"[a-z0-9_]+", normalize_text(right)))
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return safe_ratio(intersection, union)


def match_severity(expected_findings: list[ParsedFinding], actual_findings: list[ParsedFinding]) -> tuple[int, int]:
    """Align expected/actual findings by rule_id + evidence similarity (greedy one-to-one)."""
    unmatched_actual = list(range(len(actual_findings)))
    hit = 0
    total = 0

    for expected in expected_findings:
        candidates: list[tuple[float, int]] = []
        for idx in unmatched_actual:
            actual = actual_findings[idx]
            if actual.rule_id != expected.rule_id:
                continue
            score = evidence_similarity(expected.evidence, actual.evidence)
            candidates.append((score, idx))
        if not candidates:
            continue

        candidates.sort(reverse=True)
        best_score, best_idx = candidates[0]
        # Accept low-overlap matches only when there is one obvious candidate.
        if best_score < 0.15 and len(candidates) > 1:
            continue

        unmatched_actual.remove(best_idx)
        total += 1
        if actual_findings[best_idx].severity == expected.severity:
            hit += 1

    return hit, total


def score_actionability(findings: list[ParsedFinding]) -> float:
    if not findings:
        return 0.0
    good = 0
    for f in findings:
        # S2: word-boundary action word check
        has_action = bool(
            ACTION_WORDS_PATTERN.search(f.minimal_fix) or ACTION_WORDS_PATTERN.search(f.verification)
        )
        if f.minimal_fix.strip() and f.verification.strip() and has_action:
            good += 1
    return safe_ratio(good, len(findings))


def parse_expected_findings(raw_findings: list[dict[str, str]]) -> list[ParsedFinding]:
    parsed: list[ParsedFinding] = []
    for finding in raw_findings:
        parsed.append(
            ParsedFinding(
                severity=str(finding.get("severity", "")).strip(),
                rule_id=str(finding.get("rule_id", "")).strip(),
                evidence=str(finding.get("evidence", "")).strip(),
                minimal_fix=str(finding.get("minimal_fix", "")).strip(),
                verification=str(finding.get("verification", "")).strip(),
            )
        )
    return parsed


def main() -> int:
    args = parse_args()
    manifest_path = pathlib.Path(args.manifest)
    actual_dir = pathlib.Path(args.actual_dir)
    out_path = pathlib.Path(args.out)

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases = data.get("cases", [])

    script_dir = pathlib.Path(__file__).resolve().parent
    lint_script = script_dir / "skill_output_lint.py"
    lint_module = load_lint_module(lint_script)

    structure_score_sum = 0.0
    rule_f1_sum = 0.0
    rule_cases = 0
    severity_hit = 0
    severity_total = 0
    action_sum = 0.0
    action_cases = 0

    per_case: list[dict[str, object]] = []

    for case in cases:
        case_id = case["case_id"]
        expected_rel = case["expected_file"]
        expected_path = manifest_path.parent / expected_rel

        actual_path_json = actual_dir / f"{case_id}.json"
        actual_path_md = actual_dir / f"{case_id}.md"
        if actual_path_json.exists():
            actual_path = actual_path_json
        elif actual_path_md.exists():
            actual_path = actual_path_md
        else:
            # F2: Missing cases score 0 on all axes instead of being skipped
            per_case.append({"case_id": case_id, "status": "missing_actual"})
            structure_score_sum += 0.0
            rule_f1_sum += 0.0
            rule_cases += 1
            action_sum += 0.0
            action_cases += 1
            continue

        expected_findings_raw = json.loads(expected_path.read_text(encoding="utf-8")).get("findings", [])
        expected_findings = parse_expected_findings(expected_findings_raw)
        allow_empty = case.get("allow_empty_findings", False) or len(expected_findings) == 0

        lint_cmd = [sys.executable, str(lint_script), "--input", str(actual_path), "--profile", "clean-code"]
        if allow_empty:
            lint_cmd.append("--allow-empty-findings")
        lint_proc = subprocess.run(
            lint_cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        lint_code = lint_proc.returncode
        structure_case = 1.0 if lint_code == 0 else (0.5 if lint_code == 1 else 0.0)
        structure_score_sum += structure_case

        actual_findings = load_findings_via_lint(lint_module, actual_path)

        expected_rules = [f.rule_id for f in expected_findings if f.rule_id]
        actual_rules = [f.rule_id for f in actual_findings if f.rule_id]

        # S1: F1-based rule matching
        rule_f1, rule_detail = score_rule_f1(expected_rules, actual_rules)
        rule_f1_sum += rule_f1
        rule_cases += 1

        # Severity match on aligned findings (rule_id + evidence similarity).
        case_hit, case_total = match_severity(expected_findings, actual_findings)
        severity_total += case_total
        severity_hit += case_hit

        # Empty expected + empty actual = perfect actionability (no false positives)
        if not expected_findings_raw and not actual_findings:
            action_case = 1.0
        else:
            action_case = score_actionability(actual_findings)
        action_sum += action_case
        action_cases += 1

        per_case.append(
            {
                "case_id": case_id,
                "status": "scored",
                "lint_code": lint_code,
                "structure_case_score": structure_case,
                "expected_rule_count": len(expected_rules),
                "actual_rule_count": len(actual_rules),
                "rule_f1_detail": rule_detail,
                "actionability_case_score": round(action_case, 3),
            }
        )

    case_count = len(cases) if cases else 1
    scored_cases = sum(1 for c in per_case if c.get("status") == "scored")
    missing_count = case_count - scored_cases

    # F2: All denominators use case_count so missing cases are penalized (scored as 0)
    structure_points = 40.0 * safe_ratio(structure_score_sum, case_count)
    rule_points = 35.0 * safe_ratio(rule_f1_sum, case_count)
    action_points = 10.0 * safe_ratio(action_sum, case_count)

    # S3: if no shared rules exist, exclude severity from total and rescale
    if severity_total == 0:
        severity_points = 0.0
        total = structure_points + rule_points + action_points
        total = total * (100.0 / 85.0)  # rescale: 40+35+10=85 → 100
        severity_note = "severity_excluded_rescaled"
    else:
        severity_points = 15.0 * safe_ratio(severity_hit, severity_total)
        total = structure_points + rule_points + severity_points + action_points
        severity_note = None
    grade = "pass" if total >= 85 else ("warning" if total >= 70 else "fail")

    report: dict[str, object] = {
        "summary": {
            "case_count": len(cases),
            "scored_cases": scored_cases,
            "missing_cases": [c["case_id"] for c in per_case if c.get("status") == "missing_actual"],
        },
        "score": {
            "total": round(total, 2),
            "grade": grade,
            "breakdown": {
                "structure_40": round(structure_points, 2),
                "rule_f1_35": round(rule_points, 2),
                "severity_match_15": round(severity_points if severity_total > 0 else 0.0, 2),
                "actionability_10": round(action_points, 2),
            },
            "raw": {
                "rule_f1_avg": round(safe_ratio(rule_f1_sum, case_count), 3),
                "severity_hit": severity_hit,
                "severity_total": severity_total,
                "missing_cases": missing_count,
                **({"severity_note": severity_note} if severity_note else {}),
            },
        },
        "cases": per_case,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written: {out_path}")
    print(f"total: {report['score']['total']} ({report['score']['grade']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
