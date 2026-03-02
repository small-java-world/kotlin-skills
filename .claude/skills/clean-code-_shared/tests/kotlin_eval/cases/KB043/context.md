case_id: KB043
category: kotlin
difficulty: intro
source_refs: kotlinlang/null-safety, jetbrains/kotlin-null-safety

Goal: False-positive resistance test.
This code is intentionally clean and well-structured.
The correct output is an EMPTY findings list.

Notes:
- ApiClient uses safe casts (as?), elvis operators, and nullable return types.
- No unsafe casts, no lateinit abuse, no platform type leaks.
- Null boundaries are explicit and handled at the edge.
- Expected output: { "findings": [] } — zero findings, empty summary.
- This case validates that the skill does NOT flag correct null-safety patterns (CC-K003).
