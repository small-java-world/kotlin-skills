package eval.kb023

data class User(val email: String?)

class MailService {
    fun x(u: User?): String {
        val e = u!!.email!!
        return e.substringAfter("@")
    }
}
