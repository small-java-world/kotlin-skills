package eval.kb009

import java.time.LocalDateTime
import java.util.UUID
import kotlin.random.Random

class SessionTokenService {
    fun issueToken(userId: String): String {
        val now = LocalDateTime.now()
        val randomPart = Random.nextInt(1000, 9999)
        val trace = UUID.randomUUID().toString().substring(0, 8)
        return "${userId}_${now.minute}_${randomPart}_$trace"
    }
}

