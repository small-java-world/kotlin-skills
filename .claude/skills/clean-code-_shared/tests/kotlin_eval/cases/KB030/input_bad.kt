package eval.kb030

import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

class BatchNotificationService(
    private val sender: NotificationSender
) {
    // BUG: coroutineScope cancels all children when one fails
    // If sending to user 3 throws, users 4..N never get notified
    suspend fun sendAll(userIds: List<String>, message: String) = coroutineScope {
        userIds.forEach { userId ->
            launch {
                sender.send(userId, message)
            }
        }
    }

    suspend fun sendUrgent(userIds: List<String>, message: String) = coroutineScope {
        userIds.forEach { userId ->
            launch {
                sender.sendUrgent(userId, message)
                sender.logDelivery(userId)
            }
        }
    }
}

interface NotificationSender {
    suspend fun send(userId: String, message: String)
    suspend fun sendUrgent(userId: String, message: String)
    suspend fun logDelivery(userId: String)
}
