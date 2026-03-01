package eval.kb027

// Simulates a Java library class (as if it were @Nullable String getUserEmail())
// In real Java interop, the return type would be String! (platform type)
class JavaUserClient {
    // @Nullable annotation on Java side — Kotlin sees this as String!
    fun getUserEmail(userId: String): String? = null // simplified; real Java returns platform type
}

class UserNotificationService(private val javaClient: JavaUserClient) {

    fun sendWelcomeEmail(userId: String) {
        // BUG: platform type used directly without null check
        val email = javaClient.getUserEmail(userId) // type is actually String! in real interop
        val domain = email!!.substringAfter("@")    // !! bypasses null safety
        println("Sending to domain: $domain")
    }

    fun getUserInitials(userId: String): String {
        val email = javaClient.getUserEmail(userId)
        // BUG: .length accessed without null check, crashes if email is null
        return email.substring(0, 2).uppercase()
    }
}
