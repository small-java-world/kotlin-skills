case_id: KB012
category: testability
difficulty: intermediate
source_refs: kotlinlang/coding-conventions, spring-petclinic/spring-petclinic-kotlin

# Scenario
CSV parser assumes valid three-column input and has no defensive behavior.

# Goal
Detect missing boundary tests and brittle parsing design.

