case_id: KB033
category: kotlin
difficulty: advanced
source_refs: kotlinlang/flow, kotlinlang/channels

# Scenario
An event processing pipeline uses `channelFlow` with `conflate()` to handle sensor readings. The `conflate` operator silently drops intermediate values under back-pressure, causing event loss without any explicit overflow strategy or logging.

# Goal
Detect CC-K002 (implicit event loss via conflate without explicit overflow handling).

# Scoring Note
Both `processReadings` and `processAllSensors` exhibit the same bug. A single combined finding covering both methods is the expected form. An AI that raises two separate findings (one per method) is also acceptable; both should be credited as correct.
