case_id: KB014
category: change_safety
difficulty: advanced
source_refs: spring-petclinic/spring-petclinic-kotlin, square/okhttp

Goal: Detect mixed-intent migration change across two simulated files,
missing migration stage definitions, and a YAGNI leftover, then propose a
minimal staged decomposition without breaking callers.

Notes:
- This is intentionally a multi-concern case: CC-C003 (mixed intent),
  CC-C004 (missing migration stages), and CC-P002 (YAGNI leftover) all apply.
- Reviewers should treat the two "files" as a single review context.
- The dual-write repo pattern is intentional for migration but lacks a cleanup contract.
