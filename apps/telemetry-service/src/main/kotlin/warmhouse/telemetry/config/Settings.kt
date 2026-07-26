package warmhouse.telemetry.config

data class DatabaseSettings(
    val jdbcUrl: String,
    val user: String,
    val password: String,
)

data class KafkaSettings(
    val bootstrapServers: String,
    val telemetryTopic: String,
    val consumerGroup: String,
)

data class Settings(
    val host: String,
    val port: Int,
    val database: DatabaseSettings,
    val kafka: KafkaSettings,
) {
    companion object {
        fun fromEnv(): Settings = Settings(
            host = env("KTOR_HOST", "0.0.0.0"),
            port = env("KTOR_PORT", "8083").toInt(),
            database = DatabaseSettings(
                jdbcUrl = env("DATABASE_JDBC_URL", "jdbc:postgresql://localhost:5432/telemetry_db"),
                user = env("DATABASE_USER", "postgres"),
                password = env("DATABASE_PASSWORD", "postgres"),
            ),
            kafka = KafkaSettings(
                bootstrapServers = env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
                telemetryTopic = env("KAFKA_TELEMETRY_TOPIC", "telemetry"),
                consumerGroup = env("KAFKA_CONSUMER_GROUP", "telemetry-service"),
            ),
        )

        private fun env(name: String, default: String): String = System.getenv(name) ?: default
    }
}
