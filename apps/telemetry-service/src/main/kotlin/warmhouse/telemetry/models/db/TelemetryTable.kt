package warmhouse.telemetry.models.db

import org.jetbrains.exposed.dao.id.LongIdTable
import org.jetbrains.exposed.sql.kotlin.datetime.timestamp

object TelemetryData : LongIdTable("telemetry_data") {
    val deviceId = long("device_id").index()
    val value = double("value")
    val unit = varchar("unit", 20)
    val recordedAt = timestamp("recorded_at").index()
}
