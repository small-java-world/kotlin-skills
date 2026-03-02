case_id: KB039
category: kotlin
difficulty: intro
source_refs: kotlinlang/coroutines, google/structured-concurrency

Goal: False-positive resistance test.
This code is intentionally clean and well-structured.
The correct output is an EMPTY findings list.

Notes:
- WorkerManager correctly injects CoroutineScope, uses supervisorScope for isolation,
  keeps Job references, and provides proper cancellation via close().
- A reviewer that produces findings for this case is generating false positives.
- Expected output: { "findings": [] } — zero findings, empty summary.
- This case validates that the skill does NOT flag correct structured concurrency.
