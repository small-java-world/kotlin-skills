case_id: KB022
category: change_safety
difficulty: advanced
source_refs: spring-petclinic/spring-petclinic-kotlin, square/okhttp

# Scenario
Migration mixes behavior change, persistence rewrite, and speculative compatibility branch in one commit.

# Goal
Detect mixed-intent migration risk and propose staged rollout + cleanup contract.
