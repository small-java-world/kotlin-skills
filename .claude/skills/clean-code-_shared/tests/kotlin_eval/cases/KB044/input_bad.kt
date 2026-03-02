// KB044: False-positive resistance case — correct scope function usage.
// Single-level apply for initialization, no chaining, no ambiguous receivers.

package eval.kb044

class NotificationBuilder {

    fun build(
        title: String,
        body: String,
        recipient: String,
        priority: Priority = Priority.NORMAL
    ): Notification {
        return Notification().apply {
            this.title = title
            this.body = body
            this.recipient = recipient
            this.priority = priority
        }
    }
}

class Notification {
    var title: String = ""
    var body: String = ""
    var recipient: String = ""
    var priority: Priority = Priority.NORMAL
}

enum class Priority { LOW, NORMAL, HIGH, URGENT }
