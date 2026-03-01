package eval.kb022

sealed interface OrderState {
    data object Pending : OrderState
    data object Paid : OrderState
}

class LegacyOrderRepo {
    fun saveStateAsString(orderId: String, state: String) {}
}

class NewOrderRepo {
    fun saveState(orderId: String, state: OrderState) {}
}

class OrderStateMigrationService(
    private val legacyRepo: LegacyOrderRepo = LegacyOrderRepo(),
    private val newRepo: NewOrderRepo = NewOrderRepo()
) {
    fun update(orderId: String, paid: Boolean, enableFutureV3Path: Boolean): String {
        val next = if (paid) OrderState.Paid else OrderState.Pending

        // behavior + structure + rollout all mixed
        legacyRepo.saveStateAsString(orderId, if (paid) "paid_v2" else "pending_v2")
        newRepo.saveState(orderId, next)

        if (enableFutureV3Path) {
            // speculative branch (not consumed by callers yet)
            return "state-v3-ready"
        }
        return "state-v2"
    }
}
