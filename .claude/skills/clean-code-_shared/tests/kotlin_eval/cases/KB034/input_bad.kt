package eval.kb034

class ConfigurationService {

    // BUG: lateinit used for values that may legitimately be absent
    // Access before configure() throws UninitializedPropertyAccessException
    lateinit var databaseUrl: String
    lateinit var apiKey: String
    lateinit var cacheHost: String

    private var configured = false

    fun configure(props: Map<String, String>) {
        props["database.url"]?.let { databaseUrl = it }
        props["api.key"]?.let { apiKey = it }
        props["cache.host"]?.let { cacheHost = it }
        configured = true
    }

    fun getDatabaseConnection(): String {
        // Throws UninitializedPropertyAccessException if "database.url" was missing from props
        return "jdbc:postgresql://$databaseUrl/app"
    }

    fun getApiHeaders(): Map<String, String> {
        return mapOf("Authorization" to "Bearer $apiKey")
    }

    fun getCacheEndpoint(): String {
        return "$cacheHost:6379"
    }
}
