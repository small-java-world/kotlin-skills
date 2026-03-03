case_id: KB020
category: testability
difficulty: advanced
source_refs: ktorio/ktor, kotlinlang/coding-conventions

# Scenario
Flow polling loop hard-codes dispatcher and delay policy.

# Goal
Detect coroutine determinism issues and suggest testable structured boundaries.
