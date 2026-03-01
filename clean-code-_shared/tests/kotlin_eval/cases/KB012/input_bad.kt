package eval.kb012

class CsvUserParser {
    fun parse(line: String): Map<String, String> {
        val parts = line.split(",")
        val id = parts[0]
        val name = parts[1]
        val age = parts[2]
        return mapOf("id" to id, "name" to name, "age" to age)
    }
}

