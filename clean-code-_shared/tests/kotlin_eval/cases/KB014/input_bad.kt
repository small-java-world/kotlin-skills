// KB014: Multi-file schema migration with mixed intent (advanced)
// Simulates a two-file scenario: a repository and its consumer sharing a fragile dual-schema boundary.

// --- File 1: UserRepository.kt ---

data class UserV1(val id: String, val fullName: String)
data class UserV2(val id: String, val givenName: String, val familyName: String)

class UserRepository {
    private val v1Store = mutableMapOf<String, UserV1>()
    private val v2Store = mutableMapOf<String, UserV2>()

    // Dual-write: writes to both schemas simultaneously (migration in progress)
    fun save(id: String, givenName: String, familyName: String) {
        v2Store[id] = UserV2(id, givenName, familyName)
        // Legacy sync: derive fullName for old readers
        v1Store[id] = UserV1(id, "$givenName $familyName")
    }

    // Returns V1 or V2 depending on caller preference — no contract defined
    fun findV1(id: String): UserV1? = v1Store[id]
    fun findV2(id: String): UserV2? = v2Store[id]
}

// --- File 2: DisplayNameService.kt ---

class DisplayNameService(private val repo: UserRepository) {

    // Mixed intent: this method was changed to add V2 support BUT also renamed parameter
    // and changed return type in the same commit
    fun resolveDisplay(userId: String): String {
        val v2 = repo.findV2(userId)
        if (v2 != null) {
            // New behavior: title-case each name part
            return "${v2.givenName.replaceFirstChar { it.uppercaseChar() }} " +
                   "${v2.familyName.replaceFirstChar { it.uppercaseChar() }}"
        }
        // Fallback to legacy
        return repo.findV1(userId)?.fullName ?: "Unknown"
    }

    // Leftover method from V1 era — no callers remain, not deleted
    @Deprecated("Use resolveDisplay instead")
    fun getDisplayName(userId: String): String {
        return repo.findV1(userId)?.fullName ?: "Unknown"
    }
}
