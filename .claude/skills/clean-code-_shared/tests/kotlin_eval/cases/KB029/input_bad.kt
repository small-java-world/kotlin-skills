package eval.kb029

// BUG 1: var property in data class — mutable state breaks hashCode contract when used as map key
data class BaseEvent(
    var id: String,
    val type: String
)

// BUG 2: data class inheritance — equals/hashCode of ClickEvent do not match BaseEvent
// child.equals(parent) may behave asymmetrically
data class ClickEvent(
    val elementId: String,
    val timestamp: Long
) : BaseEvent(id = "", type = "CLICK")

// Usage that triggers the bug
val eventCache = mutableMapOf<BaseEvent, String>()

fun registerEvent(event: BaseEvent, handler: String) {
    eventCache[event] = handler
    event.id = "assigned-${event.type}"  // mutates key after insertion — map lookup now broken
}
