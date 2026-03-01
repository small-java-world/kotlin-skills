package eval.kb021

data class OrderDto(val id: String, val amount: Int)

class BizService {
    fun process(d: OrderDto, f: Boolean, t: String): String {
        if (f) {
            return "ok-${d.id}-${t.lowercase()}"
        }
        return "ng-${d.id}-${t.uppercase()}"
    }
}
