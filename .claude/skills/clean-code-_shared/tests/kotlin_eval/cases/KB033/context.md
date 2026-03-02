case_id: KB033
category: kotlin
difficulty: advanced
source_refs: kotlinlang/flow, kotlinlang/channels

# Scenario
An event processing pipeline uses `channelFlow` with `conflate()` to handle sensor readings. The `conflate` operator silently drops intermediate values under back-pressure, causing event loss without any explicit overflow strategy or logging.

# Goal
Detect CC-K002 (implicit event loss via conflate without explicit overflow handling).
