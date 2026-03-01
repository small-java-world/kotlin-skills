package eval.kb004

object SessionCache {
    var refreshCount: Int = 0
    val values: MutableMap<String, String> = mutableMapOf()
}

class SessionService {
    fun getSessionToken(userId: String): String {
        SessionCache.refreshCount += 1
        if (!SessionCache.values.containsKey(userId)) {
            SessionCache.values[userId] = "token-$userId-${System.currentTimeMillis()}"
        }
        return SessionCache.values[userId] ?: ""
    }
}

