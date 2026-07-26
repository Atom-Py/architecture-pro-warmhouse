package warmhouse.telemetry

import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.install
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import kotlinx.serialization.json.Json
import warmhouse.telemetry.config.Settings
import warmhouse.telemetry.infra.DatabaseFactory
import warmhouse.telemetry.integrations.kafka.TelemetryConsumer
import warmhouse.telemetry.web.configureRouting

fun main() {
    val settings = Settings.fromEnv()

    DatabaseFactory.connect(settings.database)

    val consumer = TelemetryConsumer(settings.kafka)
    consumer.start()

    embeddedServer(Netty, host = settings.host, port = settings.port) {
        install(ContentNegotiation) {
            json(
                Json {
                    ignoreUnknownKeys = true
                    encodeDefaults = true
                },
            )
        }
        configureRouting()
    }.start(wait = true)
}
