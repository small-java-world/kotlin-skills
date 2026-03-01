Case_ID: KB009
Category: testability
Difficulty: intro
Source_Refs: square/okhttp, kotlinlang/coding-conventions

# Scenario
Token generation reads wall clock and random sources directly, making tests nondeterministic.

# Goal
Detect deterministic-testability issues.

