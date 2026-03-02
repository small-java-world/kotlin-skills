case_id: KB045
category: kotlin
difficulty: intro
source_refs: kotlinlang/data-classes, kotlinlang/coding-conventions

Goal: False-positive resistance test.
This code is intentionally clean and well-structured.
The correct output is an EMPTY findings list.

Notes:
- Data class with val-only properties (immutable, safe for hashCode/equals).
- Validation in init block ensures copy() also enforces invariants.
- No inheritance, no mutable state, no contract violations.
- Expected output: { "findings": [] } — zero findings, empty summary.
- This case validates that the skill does NOT flag correct data class design (CC-K005).
