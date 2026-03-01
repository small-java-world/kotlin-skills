package eval.kb019

import java.time.Instant
import kotlin.random.Random

class SessionTokenService {
    fun issue(userId: String): String {
        val issuedAt = Instant.now().epochSecond
        val entropy = Random.nextInt(1000, 9999)
        return "$userId-$issuedAt-$entropy"
    }
}
