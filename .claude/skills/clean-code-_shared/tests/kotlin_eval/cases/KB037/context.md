Case_ID: KB037
Category: kotlin
Difficulty: intermediate
Source_Refs: kotlinlang/data-classes, kotlinlang/coding-conventions

# Scenario
A data class has a companion factory method with validation, but the auto-generated `copy()` method bypasses that validation entirely. Callers can create invalid instances via `copy()`.

# Goal
Detect CC-K005 (copy() bypasses factory validation in data class).
