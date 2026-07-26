package warmhouse.telemetry.infra

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import org.jetbrains.exposed.sql.Database
import org.jetbrains.exposed.sql.SchemaUtils
import org.jetbrains.exposed.sql.transactions.transaction
import warmhouse.telemetry.config.DatabaseSettings
import warmhouse.telemetry.models.db.TelemetryData

object DatabaseFactory {
    fun connect(settings: DatabaseSettings) {
        val dataSource = HikariDataSource(
            HikariConfig().apply {
                jdbcUrl = settings.jdbcUrl
                username = settings.user
                password = settings.password
                maximumPoolSize = 5
            },
        )
        Database.connect(dataSource)
        transaction {
            SchemaUtils.create(TelemetryData)
        }
    }
}
