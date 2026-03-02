// KB043: False-positive resistance case — correct null-safety patterns.
// ApiClient uses safe casts, elvis operators, and nullable return types.

package eval.kb043

class ApiResponseParser {

    fun parseUser(raw: Any?): UserDto? {
        val map = raw as? Map<*, *> ?: return null
        val name = map["name"] as? String ?: return null
        val age = (map["age"] as? Number)?.toInt() ?: return null
        val city = (map["address"] as? Map<*, *>)
            ?.get("city") as? String
        return UserDto(name = name, age = age, city = city)
    }

    fun parseUsers(raw: Any?): List<UserDto> {
        val list = raw as? List<*> ?: return emptyList()
        return list.mapNotNull { parseUser(it) }
    }
}

data class UserDto(val name: String, val age: Int, val city: String?)
