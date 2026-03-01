case_id: KB015
category: principles
difficulty: intro
source_refs: kotlinlang/coding-conventions

Goal: False-positive resistance test.
This code is intentionally clean and well-structured.
The correct output is an EMPTY findings list.

Notes:
- PricingCalculator is a pure function with no side effects, no global state,
  no speculative abstractions, and no SRP violations.
- A reviewer that produces findings for this case is generating false positives.
- Expected output: { "findings": [] } — zero findings, empty summary.
- This case validates that the skill does NOT flag clean code.
