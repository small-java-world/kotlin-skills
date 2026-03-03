case_id: KB026
category: kotlin
difficulty: intermediate
source_refs: kotlinlang/flow, google/android-codelabs

# Scenario
A repository function returns a cold Flow, which is then shared via shareIn with replay=0. Downstream collectors that subscribe late will miss emitted events, causing silent data loss.

# Goal
Detect CC-K002 (Flow cold/hot misuse with replay=0) and propose correct replay configuration.
