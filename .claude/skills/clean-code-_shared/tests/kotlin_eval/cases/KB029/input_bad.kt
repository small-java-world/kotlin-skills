package eval.kb029

// BUG 1: data class with var property used as map key
// var id means hashCode changes after mutation → silent map corruption
data class CacheKey(
    var id: String,
    val category: String
)

// BUG 2: data class extending open class — equals/hashCode contract violation
// ClickEvent.equals only considers elementId + timestamp,
// ignoring id and type from BaseEvent → semantically different events may compare equal
open class BaseEvent(
    val id: String,
    val type: String
)

data class ClickEvent(
    val elementId: String,
    val timestamp: Long
) : BaseEvent(id = "", type = "CLICK")

// Usage that triggers BUG 1
val keyCache = mutableMapOf<CacheKey, String>()

fun registerKey(key: CacheKey, handler: String) {
    keyCache[key] = handler
    key.id = "resolved-${key.category}"  // mutates key after insertion — map lookup now broken
}
