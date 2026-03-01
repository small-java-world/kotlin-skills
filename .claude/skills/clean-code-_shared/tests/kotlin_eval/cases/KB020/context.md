Case_ID: KB020
Category: testability
Difficulty: advanced
Source_Refs: ktorio/ktor, kotlinlang/coding-conventions

# Scenario
Flow polling loop hard-codes dispatcher and delay policy.

# Goal
Detect coroutine determinism issues and suggest testable structured boundaries.
