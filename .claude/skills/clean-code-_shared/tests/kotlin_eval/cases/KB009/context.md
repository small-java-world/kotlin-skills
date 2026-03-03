case_id: KB009
category: testability
difficulty: intro
source_refs: square/okhttp, kotlinlang/coding-conventions

# Scenario
Token generation reads wall clock and random sources directly, making tests nondeterministic.

# Goal
Detect deterministic-testability issues.

