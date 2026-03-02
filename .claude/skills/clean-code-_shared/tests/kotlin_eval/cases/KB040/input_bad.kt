// KB040: False-positive resistance case — correct Repository pattern.
// Interface + implementation split, SRP, proper null handling.

package eval.kb040

interface UserRepository {
    suspend fun findById(id: String): User?
    suspend fun findByEmail(email: String): User?
    suspend fun findAll(): List<User>
}

class UserRepositoryImpl(
    private val dataSource: UserDataSource
) : UserRepository {

    override suspend fun findById(id: String): User? {
        return dataSource.queryById(id)
    }

    override suspend fun findByEmail(email: String): User? {
        return dataSource.queryByEmail(email)
    }

    override suspend fun findAll(): List<User> {
        return dataSource.queryAll()
    }
}

data class User(val id: String, val name: String, val email: String)

interface UserDataSource {
    suspend fun queryById(id: String): User?
    suspend fun queryByEmail(email: String): User?
    suspend fun queryAll(): List<User>
}
