case_id: KB013
category: principles
difficulty: advanced
source_refs: ktorio/ktor, spring-petclinic/spring-petclinic-kotlin

Goal: Detect multiple overlapping principle violations (SRP + KISS + change-safety blast radius)
in a single orchestration class, and propose a minimal staged decomposition.

Notes:
- This case intentionally combines SRP (domain + transport + audit in one method),
  KISS (early-return response formatting mixed into business flow),
  and a change-safety concern (no compensation boundary for partial failures).
- Reviewers should map each hot spot to the primary violated rule without over-splitting
  into one finding per line.
