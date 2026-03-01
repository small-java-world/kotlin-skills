Case_ID: KB019
Category: testability
Difficulty: intro
Source_Refs: kotlinlang/coding-conventions, detekt/style-rules

# Scenario
Token issuance uses wall clock and random source directly inside domain logic.

# Goal
Detect non-determinism boundary issues and propose minimal seams for deterministic tests.
