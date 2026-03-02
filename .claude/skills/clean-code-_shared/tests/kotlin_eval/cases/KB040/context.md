case_id: KB040
category: principles
difficulty: intro
source_refs: kotlinlang/coding-conventions

Goal: False-positive resistance test.
This code is intentionally clean and well-structured.
The correct output is an EMPTY findings list.

Notes:
- UserRepository follows interface-segregation with a clean interface/implementation split.
- Single responsibility: read operations only, no side effects in queries.
- Proper null handling with nullable return types.
- Expected output: { "findings": [] } — zero findings, empty summary.
- This case validates that the skill does NOT flag a correct Repository pattern.
