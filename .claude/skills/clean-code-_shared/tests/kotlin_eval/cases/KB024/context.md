case_id: KB024
category: testability
difficulty: intermediate
source_refs: kotlinlang/coding-conventions, detekt/style-rules

# Scenario
Blocking wrapper uses runBlocking + real delay and encourages sleep-based tests.

# Goal
Detect deterministic testability issues in coroutine bridge code.
