Case_ID: KB024
Category: testability
Difficulty: intermediate
Source_Refs: kotlinlang/coding-conventions, detekt/style-rules

# Scenario
Blocking wrapper uses runBlocking + real delay and encourages sleep-based tests.

# Goal
Detect deterministic testability issues in coroutine bridge code.
