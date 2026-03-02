case_id: KB041
category: testability
difficulty: intro
source_refs: kotlinlang/coding-conventions

Goal: False-positive resistance test.
This code is intentionally clean and well-structured.
The correct output is an EMPTY findings list.

Notes:
- AuditLogger injects Clock for deterministic time in tests.
- No hardcoded System.currentTimeMillis() or LocalDateTime.now().
- Single responsibility: only formats and writes audit entries.
- Expected output: { "findings": [] } — zero findings, empty summary.
- This case validates that the skill does NOT flag a Clock-injected testable service.
