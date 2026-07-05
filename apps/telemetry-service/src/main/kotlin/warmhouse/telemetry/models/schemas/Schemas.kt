package warmhouse.telemetry.models.schemas

import kotlinx.datetime.Instant
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class TelemetryEvent(
    @SerialName("device_id") val deviceId: Long,
    val value: Double,
    val unit: String = "",
    @SerialName("recorded_at") val recordedAt: Instant? = null,
)

@Serializable
data class TelemetryRecord(
    val id: Long,
    @SerialName("device_id") val deviceId: Long,
    val value: Double,
    val unit: String,
    @SerialName("recorded_at") val recordedAt: Instant,
)

@Serializable
data class TelemetryHistoryResponse(
    @SerialName("device_id") val deviceId: Long,
    val items: List<TelemetryRecord>,
)

@Serializable
data class ErrorResponse(
    val code: String,
    val message: String,
)

@Serializable
data class HealthResponse(
    val status: String = "ok",
)
