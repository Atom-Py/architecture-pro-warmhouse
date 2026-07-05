package warmhouse.telemetry.web

import io.ktor.http.HttpStatusCode
import io.ktor.server.application.Application
import io.ktor.server.request.receive
import io.ktor.server.response.respond
import io.ktor.server.routing.get
import io.ktor.server.routing.post
import io.ktor.server.routing.route
import io.ktor.server.routing.routing
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.datetime.Instant
import warmhouse.telemetry.models.schemas.ErrorResponse
import warmhouse.telemetry.models.schemas.HealthResponse
import warmhouse.telemetry.models.schemas.TelemetryEvent
import warmhouse.telemetry.models.schemas.TelemetryHistoryResponse
import warmhouse.telemetry.services.TelemetryService

fun Application.configureRouting() {
    routing {
        get("/health") {
            call.respond(HealthResponse())
        }

        route("/api/v1") {
            post("/telemetry") {
                val event = try {
                    call.receive<TelemetryEvent>()
                } catch (exception: Exception) {
                    call.respond(
                        HttpStatusCode.BadRequest,
                        ErrorResponse("validation_error", exception.message ?: "invalid body"),
                    )
                    return@post
                }
                val record = withContext(Dispatchers.IO) { TelemetryService.save(event) }
                call.respond(HttpStatusCode.Created, record)
            }

            get("/devices/{deviceId}/telemetry/latest") {
                val deviceId = call.parameters["deviceId"]?.toLongOrNull()
                if (deviceId == null) {
                    call.respond(HttpStatusCode.BadRequest, ErrorResponse("validation_error", "invalid device id"))
                    return@get
                }
                val record = withContext(Dispatchers.IO) { TelemetryService.latest(deviceId) }
                if (record == null) {
                    call.respond(
                        HttpStatusCode.NotFound,
                        ErrorResponse("telemetry_not_found", "no telemetry for device $deviceId"),
                    )
                    return@get
                }
                call.respond(record)
            }

            get("/devices/{deviceId}/telemetry") {
                val deviceId = call.parameters["deviceId"]?.toLongOrNull()
                if (deviceId == null) {
                    call.respond(HttpStatusCode.BadRequest, ErrorResponse("validation_error", "invalid device id"))
                    return@get
                }
                val from = call.request.queryParameters["from"]?.let(::parseInstant)
                val to = call.request.queryParameters["to"]?.let(::parseInstant)
                if (from == null || to == null || from >= to) {
                    call.respond(
                        HttpStatusCode.BadRequest,
                        ErrorResponse("invalid_period", "'from' must be before 'to', both in ISO-8601"),
                    )
                    return@get
                }
                val limit = call.request.queryParameters["limit"]?.toIntOrNull()?.coerceIn(1, 10_000) ?: 1_000
                val items = withContext(Dispatchers.IO) { TelemetryService.history(deviceId, from, to, limit) }
                call.respond(TelemetryHistoryResponse(deviceId, items))
            }
        }
    }
}

private fun parseInstant(raw: String): Instant? = try {
    Instant.parse(raw)
} catch (_: IllegalArgumentException) {
    null
}
