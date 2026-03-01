package eval.kb010

import java.io.File
import java.net.HttpURLConnection
import java.net.URL

class UserSyncService {
    fun syncUsers(endpoint: String, outputPath: String): Int {
        val connection = URL(endpoint).openConnection() as HttpURLConnection
        connection.requestMethod = "GET"
        val body = connection.inputStream.bufferedReader().use { it.readText() }

        File(outputPath).appendText(body)
        return body.length
    }
}

