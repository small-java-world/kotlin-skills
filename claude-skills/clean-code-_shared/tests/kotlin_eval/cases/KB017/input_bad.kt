// KB017: CQS violation — methods that mutate state and return query results (CC-P005)

data class Account(val id: String, var balance: Double, var lastTransaction: String)

class AccountService {
    private val accounts = mutableMapOf<String, Account>()

    // Violates CQS: deposits money AND returns the new balance
    fun deposit(accountId: String, amount: Double): Double {
        val account = accounts[accountId] ?: throw IllegalArgumentException("Account not found")
        account.balance += amount
        account.lastTransaction = "deposit:$amount"
        return account.balance
    }

    // Violates CQS: withdraws money AND returns success/failure with remaining balance
    fun withdraw(accountId: String, amount: Double): Pair<Boolean, Double> {
        val account = accounts[accountId] ?: throw IllegalArgumentException("Account not found")
        if (account.balance < amount) {
            return Pair(false, account.balance)
        }
        account.balance -= amount
        account.lastTransaction = "withdraw:$amount"
        return Pair(true, account.balance)
    }

    // Violates CQS: transfers between accounts AND returns a status string
    fun transfer(fromId: String, toId: String, amount: Double): String {
        val result = withdraw(fromId, amount)
        if (!result.first) {
            return "INSUFFICIENT_FUNDS:${result.second}"
        }
        val newBalance = deposit(toId, amount)
        return "OK:$newBalance"
    }

    fun getBalance(accountId: String): Double {
        return accounts[accountId]?.balance ?: throw IllegalArgumentException("Account not found")
    }
}
