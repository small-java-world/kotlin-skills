// KB041: False-positive resistance case — Clock-injected testable service.
// AuditLogger uses injected Clock, no hardcoded time sources.

package eval.kb041

import java.time.Clock
import java.time.Instant

class AuditLogger(
    private val clock: Clock,
    private val writer: AuditWriter
) {
    fun log(action: String, userId: String) {
        val timestamp = Instant.now(clock)
        val entry = AuditEntry(
            timestamp = timestamp,
            action = action,
            userId = userId
        )
        writer.write(entry)
    }
}

data class AuditEntry(
    val timestamp: Instant,
    val action: String,
    val userId: String
)

interface AuditWriter {
    fun write(entry: AuditEntry)
}
