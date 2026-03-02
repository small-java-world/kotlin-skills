package eval.kb038

// BUG: data class inheriting from open class breaks equals/hashCode
// Parent fields (type, timestamp) are excluded from generated equals/hashCode
open class DomainEvent(
    val type: String,
    val timestamp: Long = System.currentTimeMillis()
)

// equals/hashCode only considers `orderId` and `amount`, ignoring `type` and `timestamp`
data class OrderPlaced(
    val orderId: String,
    val amount: Long
) : DomainEvent("ORDER_PLACED")

data class OrderCancelled(
    val orderId: String,
    val reason: String
) : DomainEvent("ORDER_CANCELLED")

// Asymmetric equality: two events with different timestamps are "equal"
// Set<DomainEvent> deduplication fails silently
class EventStore {
    private val events = mutableSetOf<DomainEvent>()

    fun store(event: DomainEvent) {
        events.add(event)  // may silently drop events with same orderId
    }

    fun findByOrderId(orderId: String): List<DomainEvent> {
        return events.filter {
            when (it) {
                is OrderPlaced -> it.orderId == orderId
                is OrderCancelled -> it.orderId == orderId
                else -> false
            }
        }
    }

    fun count(): Int = events.size
}
