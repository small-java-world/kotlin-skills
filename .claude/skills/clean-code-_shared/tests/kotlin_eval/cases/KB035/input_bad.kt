package eval.kb035

class JsonResponseParser {

    // BUG: unsafe `as` casts bypass null safety
    // ClassCastException at runtime if structure differs from expectation
    fun parseUserProfile(raw: Any): UserProfile {
        val map = raw as Map<String, Any>  // crashes if raw is not a Map
        val name = map["name"] as String   // crashes if name is null or not String
        val age = map["age"] as Int        // crashes if age is missing or Double
        val address = map["address"] as Map<String, Any>
        val city = address["city"] as String

        return UserProfile(name, age, city)
    }

    fun parseUserList(raw: Any): List<UserProfile> {
        val list = raw as List<Map<String, Any>>  // unsafe cast of nested generic
        return list.map { item ->
            val name = item["name"] as String
            val age = item["age"] as Int
            val city = (item["address"] as Map<String, Any>)["city"] as String
            UserProfile(name, age, city)
        }
    }
}

data class UserProfile(val name: String, val age: Int, val city: String)
