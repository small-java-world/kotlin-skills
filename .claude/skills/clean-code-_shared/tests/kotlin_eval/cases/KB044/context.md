case_id: KB044
category: kotlin
difficulty: intro
source_refs: kotlinlang/scope-functions, jetbrains/kotlin-idioms

Goal: False-positive resistance test.
This code is intentionally clean and well-structured.
The correct output is an EMPTY findings list.

Notes:
- Single-level scope function usage (apply only) for object initialization.
- No chaining beyond one level, no ambiguous `it` references.
- Standard idiomatic Kotlin builder pattern.
- Expected output: { "findings": [] } — zero findings, empty summary.
- This case validates that the skill does NOT flag correct scope function usage (CC-K004).
