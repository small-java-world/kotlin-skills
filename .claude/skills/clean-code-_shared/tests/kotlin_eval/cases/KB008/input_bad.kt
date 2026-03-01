package eval.kb008

data class LegacyUser(val id: String, val displayName: String)
data class NewUser(val id: String, val firstName: String, val lastName: String)

class UserMapper {
    fun toDisplayName(legacy: LegacyUser?, modern: NewUser?): String {
        if (modern != null) return "${modern.firstName} ${modern.lastName}"
        if (legacy != null) return legacy.displayName
        return "unknown"
    }
}

class UserMigrationService(private val mapper: UserMapper) {
    fun readDisplayName(legacy: LegacyUser?, modern: NewUser?): String {
        // Temporary dual-read path with no migration contract.
        return mapper.toDisplayName(legacy, modern)
    }
}

