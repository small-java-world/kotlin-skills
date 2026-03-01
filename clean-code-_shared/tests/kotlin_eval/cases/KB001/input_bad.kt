package eval.kb001

data class UpdateProfileRequest(
    val userId: String,
    val name: String,
    val email: String,
    val newsletter: Boolean
)

class UserRepo {
    fun save(userId: String, name: String, email: String, newsletter: Boolean) = true
}

class AuditLog {
    fun write(message: String) {
        println(message)
    }
}

class UserProfileController(
    private val userRepo: UserRepo,
    private val auditLog: AuditLog
) {
    fun updateProfile(req: UpdateProfileRequest): Map<String, Any> {
        if (req.userId.isBlank()) return mapOf("status" to 400, "error" to "userId required")
        if (!req.email.contains("@")) return mapOf("status" to 400, "error" to "invalid email")
        if (req.name.length > 30) return mapOf("status" to 400, "error" to "name too long")

        val saved = userRepo.save(req.userId, req.name.trim(), req.email.lowercase(), req.newsletter)
        auditLog.write("updated profile user=${req.userId} email=${req.email}")

        return if (saved) {
            mapOf("status" to 200, "message" to "updated", "user" to req.userId)
        } else {
            mapOf("status" to 500, "error" to "failed to save")
        }
    }
}

