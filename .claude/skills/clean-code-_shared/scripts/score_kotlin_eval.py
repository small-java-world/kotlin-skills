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
# NOTE: Duplicated from skill_output_lint.py — keep in sync (TODO: extract to shared module)
ACTION_WORDS_PATTERN = re.compile(
    r"\b(?:add|extract|split|remove|introduce|replace|rename|run|assert|test|verify|"
    r"追加|抽出|分離|削除|置換|実行|検証|確認)\b",
    re.IGNORECASE,
)

# S3: Backtick-enclosed identifiers or CamelCase identifiers in fix/verification text
CODE_IDENTIFIER_PATTERN = re.compile(
    r"`[^`]+`|[A-Z][a-z]+[A-Z][a-zA-Z0-9]*|[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]+"
)


@dataclass
class ParsedFinding:
    severity: str
    rule_id: str
    evidence: str
    minimal_fix: str
    verification: str
    file: str = ""        # optional: relative path of the reviewed file
    line_range: str = ""  # optional: problem line range e.g. "42-58" or "42"


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
            file=getattr(f, "file", ""),
            line_range=getattr(f, "line_range", ""),
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


def _tokenize(text: str) -> set[str]:
    # ASCII identifiers + Japanese character blocks (hiragana/katakana/kanji)
    ascii_tokens = set(re.findall(r"[a-z0-9_]+", normalize_text(text)))
    ja_tokens = set(re.findall(r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]+", text))
    return ascii_tokens | ja_tokens


def _extract_code_anchors(text: str) -> set[str]:
    """Extract backtick-enclosed identifiers and CamelCase tokens from evidence."""
    backticks = set(re.findall(r"`([^`]+)`", text))
    camels = set(re.findall(
        r"[A-Z][a-z]+[A-Z][a-zA-Z0-9]*|[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]+",
        text,
    ))
    return {a.lower() for a in (backticks | camels)}


def evidence_similarity(left: str, right: str) -> float:
    """Weighted Jaccard: code anchors count 1.5x more than plain tokens (0.6 vs 0.4 weight)."""
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens and not right_tokens:
        return 0.0  # Empty evidence is undefined, not similar
    if not left_tokens or not right_tokens:
        return 0.0

    # Base Jaccard on plain tokens
    base_intersection = len(left_tokens & right_tokens)
    base_union = len(left_tokens | right_tokens)
    base_jaccard = safe_ratio(base_intersection, base_union)

    # Code anchor bonus: anchors matching boosts similarity
    left_anchors = _extract_code_anchors(left)
    right_anchors = _extract_code_anchors(right)
    if left_anchors and right_anchors:
        anchor_intersection = len(left_anchors & right_anchors)
        anchor_union = len(left_anchors | right_anchors)
        anchor_jaccard = safe_ratio(anchor_intersection, anchor_union)
        # Weighted: 40% base tokens + 60% code anchors
        return 0.4 * base_jaccard + 0.6 * anchor_jaccard

    return base_jaccard


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
        # Require minimum similarity regardless of candidate count.
        # rule_id-only match with no evidence overlap likely points to a different
        # problem under the same rule, not the same finding rephrased.
        if best_score < 0.15:
            continue

        unmatched_actual.remove(best_idx)
        total += 1
        if actual_findings[best_idx].severity == expected.severity:
            hit += 1

    return hit, total


def score_actionability(findings: list[ParsedFinding]) -> float:
    if not findings:
        return 0.0
    scores: list[float] = []
    for f in findings:
        # S2: word-boundary action word check
        has_action = bool(
            ACTION_WORDS_PATTERN.search(f.minimal_fix) or ACTION_WORDS_PATTERN.search(f.verification)
        )
        # S3: code identifier check — fix and verification should reference concrete code
        has_identifier = bool(
            CODE_IDENTIFIER_PATTERN.search(f.minimal_fix) or CODE_IDENTIFIER_PATTERN.search(f.verification)
        )
        if not (f.minimal_fix.strip() and f.verification.strip() and has_action):
            scores.append(0.0)
        else:
            scores.append(1.0 if has_identifier else 0.85)
    return safe_ratio(sum(scores), len(scores))


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
                file=str(finding.get("file", "")).strip(),
                line_range=str(finding.get("line_range", "")).strip(),
            )
        )
    return parsed


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _normalize_path(path_text: str) -> str:
    return _normalize_space(path_text).replace("\\", "/").lower()


def findings_signature(findings: list[ParsedFinding]) -> tuple[tuple[str, ...], ...]:
    """Canonical signature for semantic equality across JSON/Markdown outputs."""
    normalized: list[tuple[str, ...]] = []
    for f in findings:
        normalized.append(
            (
                f.rule_id.strip().upper(),
                f.severity.strip().lower(),
                _normalize_path(f.file),
                _normalize_space(f.line_range),
                _normalize_space(f.evidence),
                _normalize_space(f.minimal_fix),
                _normalize_space(f.verification),
            )
        )
    return tuple(sorted(normalized))


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
    severity_hit = 0
    severity_total = 0
    total_expected_rule_count = 0
    action_sum = 0.0

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
            action_sum += 0.0
            continue

        expected_json = json.loads(expected_path.read_text(encoding="utf-8"))
        if "findings" not in expected_json:
            print(f"ERROR: expected file missing 'findings' key: {expected_path}")
            return 2
        expected_findings_raw = expected_json["findings"]
        expected_findings = parse_expected_findings(expected_findings_raw)
        allow_empty = case.get("allow_empty_findings", False) or len(expected_findings) == 0
        expected_rules = [f.rule_id for f in expected_findings if f.rule_id]

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

        # lint ERROR (exit 2) = structurally broken output; freeze other axes at 0
        if lint_code == 2:
            total_expected_rule_count += len(expected_rules)
            per_case.append(
                {
                    "case_id": case_id,
                    "status": "scored",
                    "lint_code": lint_code,
                    "structure_case_score": structure_case,
                    "expected_rule_count": len(expected_rules),
                    "actual_rule_count": 0,
                    "rule_f1_detail": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
                    "actionability_case_score": 0.0,
                    "note": "lint_error_axes_frozen",
                }
            )
            continue

        actual_findings = load_findings_via_lint(lint_module, actual_path)

        actual_rules = [f.rule_id for f in actual_findings if f.rule_id]

        # S1: F1-based rule matching
        rule_f1, rule_detail = score_rule_f1(expected_rules, actual_rules)
        rule_f1_sum += rule_f1
        total_expected_rule_count += len(expected_rules)

        # Severity match on aligned findings (rule_id + evidence similarity).
        case_hit, case_total = match_severity(expected_findings, actual_findings)
        severity_total += case_total
        severity_hit += case_hit

        # False-positive cases: expected=empty
        if not expected_findings_raw:
            # Empty actual = perfect (correctly produced no findings)
            # Non-empty actual = 0.0 (false positives should not score well on actionability)
            action_case = 1.0 if not actual_findings else 0.0
        else:
            action_case = score_actionability(actual_findings)
        action_sum += action_case

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

    if not cases:
        print("ERROR: manifest contains no cases")
        return 2
    case_count = len(cases)
    scored_cases = sum(1 for c in per_case if c.get("status") == "scored")
    missing_count = case_count - scored_cases

    # F2: All denominators use case_count so missing cases are penalized (scored as 0)
    structure_points = 25.0 * safe_ratio(structure_score_sum, case_count)
    rule_points = 35.0 * safe_ratio(rule_f1_sum, case_count)
    action_points = 25.0 * safe_ratio(action_sum, case_count)

    # Severity scoring: if no matched findings exist, severity gets 0 (not rescaled)
    severity_points = 15.0 * safe_ratio(severity_hit, severity_total) if severity_total > 0 else 0.0
    total = structure_points + rule_points + severity_points + action_points
    if severity_total == 0 and scored_cases > 0:
        if total_expected_rule_count == 0:
            # All expected findings were empty (false-positive corpus) — severity is N/A, award full 15
            severity_points = 15.0
            total = structure_points + rule_points + severity_points + action_points
            severity_note = "severity_all_empty_findings"
        else:
            # Expected findings exist but AI produced no matching rule_ids — do not award
            severity_note = "severity_no_rule_overlap"
    else:
        severity_note = None
    grade = "pass" if total >= 85 else ("warning" if total >= 70 else "fail")

    # Detect gold-vs-gold mode by semantic findings comparison (format-agnostic).
    # This allows JSON expected vs Markdown actual when findings are equivalent.
    _identical_count = 0
    _checked_count = 0
    for c in cases:
        case_id = c["case_id"]
        ap_json = actual_dir / f"{case_id}.json"
        ap_md = actual_dir / f"{case_id}.md"
        ep = manifest_path.parent / c["expected_file"]
        if ap_json.exists() and ep.exists():
            _checked_count += 1
            try:
                expected_payload = json.loads(ep.read_text(encoding="utf-8"))
                expected_raw = expected_payload.get("findings")
                if not isinstance(expected_raw, list):
                    raise ValueError("expected file must contain findings[]")
                expected_findings_gvg = parse_expected_findings(expected_raw)
                actual_findings_json = load_findings_via_lint(lint_module, ap_json)
                if findings_signature(actual_findings_json) == findings_signature(expected_findings_gvg):
                    _identical_count += 1
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                pass  # Parse/contract mismatch — treat as not identical
        elif ap_md.exists() and ep.exists():
            _checked_count += 1
            try:
                expected_payload = json.loads(ep.read_text(encoding="utf-8"))
                expected_raw = expected_payload.get("findings")
                if not isinstance(expected_raw, list):
                    raise ValueError("expected file must contain findings[]")
                expected_findings_gvg = parse_expected_findings(expected_raw)
                actual_findings_md = load_findings_via_lint(lint_module, ap_md)
                if findings_signature(actual_findings_md) == findings_signature(expected_findings_gvg):
                    _identical_count += 1
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                pass
    scoring_mode = "gold-vs-gold" if _checked_count > 0 and _identical_count == _checked_count else "ai-vs-gold"

    report: dict[str, object] = {
        "summary": {
            "case_count": len(cases),
            "scored_cases": scored_cases,
            "missing_cases": [c["case_id"] for c in per_case if c.get("status") == "missing_actual"],
            "mode": scoring_mode,
            "mode_note": (
                "gold-vs-gold: baseline_actual contains copies of expected findings; "
                "score reflects format consistency, not AI skill performance"
                if scoring_mode == "gold-vs-gold"
                else "ai-vs-gold: baseline_actual contains real AI outputs scored against expected findings"
            ),
        },
        "score": {
            "total": round(total, 2),
            "grade": grade,
            "breakdown": {
                "structure_25": round(structure_points, 2),
                "rule_f1_35": round(rule_points, 2),
                "severity_match_15": round(severity_points, 2),
                "actionability_25": round(action_points, 2),
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
