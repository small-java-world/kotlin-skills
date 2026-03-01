Case_ID: KB012
Category: testability
Difficulty: intermediate
Source_Refs: kotlinlang/coding-conventions, spring-petclinic/spring-petclinic-kotlin

# Scenario
CSV parser assumes valid three-column input and has no defensive behavior.

# Goal
Detect missing boundary tests and brittle parsing design.

