case_id: KB007
category: change_safety
difficulty: intermediate
source_refs: ktorio/ktor, detekt/style-rules

# Scenario
Global runtime flags change behavior across modules without explicit dependency wiring.

# Goal
Detect hidden coupling and unsafe change propagation.

