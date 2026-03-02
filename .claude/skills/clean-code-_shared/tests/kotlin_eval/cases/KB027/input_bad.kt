package eval.kb027

/**
 * Wraps a legacy Java DAO (com.example.legacy.UserDao).
 * Original Java signature: public String getUserEmail(String userId) — no @Nullable annotation.
 * Kotlin auto-imports this as String! (platform type).
 *
 * Simulated here as returning non-null String to mirror platform type behaviour:
 * the compiler treats the value as non-null, but Java can return null at runtime.
 */
class LegacyUserDao {
    // Platform type simulation: Java returns String! — Kotlin trusts it as non-null
    fun findEmailById(id: String): String = throw UnsupportedOperationException("Java stub")
}

class UserNotificationService(private val dao: LegacyUserDao) {

    fun sendWelcomeEmail(userId: String) {
        // BUG: platform-type return used without null boundary;
        // if Java returns null → NPE on .substringAfter()
        val email = dao.findEmailById(userId)
        val domain = email.substringAfter("@")
        println("Sending welcome email to $domain")
    }

    fun getUserInitials(userId: String): String {
        val email = dao.findEmailById(userId)
        // BUG: no null guard — .substring crashes if Java side returns null
        return email.substring(0, 2).uppercase()
    }
}
