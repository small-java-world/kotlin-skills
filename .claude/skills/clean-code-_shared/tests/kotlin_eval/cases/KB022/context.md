Case_ID: KB022
Category: change_safety
Difficulty: advanced
Source_Refs: spring-petclinic/spring-petclinic-kotlin, square/okhttp

# Scenario
Migration mixes behavior change, persistence rewrite, and speculative compatibility branch in one commit.

# Goal
Detect mixed-intent migration risk and propose staged rollout + cleanup contract.
