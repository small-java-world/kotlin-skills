case_id: KB032
category: kotlin
difficulty: intermediate
source_refs: kotlinlang/flow, kotlinlang/stateflow

# Scenario
A dashboard view model collects a StateFlow and performs a database write (side effect) inside the `collect` lambda. If the collector restarts (e.g., screen rotation), the side effect executes again for the same state, causing duplicate writes.

# Goal
Detect CC-K002 (side effect inside StateFlow collect causing duplicate execution) and CC-P005 (CQS violation mixing query and command).
