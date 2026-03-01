Case_ID: KB018
Category: testability
Difficulty: intro
Source_Refs: kotlinlang/coding-conventions

# KB018 Context

Email validation utility with existing tests. The tests pass but have poor naming, vague assertions, and don't clearly express what behavior is being verified.

## Review Focus
- Identify tests whose names don't describe the scenario or expected outcome.
- Flag assertions that don't verify specific behavior (magic numbers, toString, isNotEmpty).
