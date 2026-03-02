case_id: KB042
category: kotlin
difficulty: intro
source_refs: kotlinlang/flow, kotlinlang/stateflow

Goal: False-positive resistance test.
This code is intentionally clean and well-structured.
The correct output is an EMPTY findings list.

Notes:
- EventBus uses SharedFlow with replay=1 and proper buffer overflow strategy.
- Collector does not perform side effects — only transforms data.
- No conflate, no silent event loss, explicit overflow handling.
- Expected output: { "findings": [] } — zero findings, empty summary.
- This case validates that the skill does NOT flag correct Flow/Channel usage (CC-K002).
