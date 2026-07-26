package warmhouse.telemetry.services

import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import org.jetbrains.exposed.sql.ResultRow
import org.jetbrains.exposed.sql.SortOrder
import org.jetbrains.exposed.sql.and
import org.jetbrains.exposed.sql.insertAndGetId
import org.jetbrains.exposed.sql.selectAll
import org.jetbrains.exposed.sql.transactions.transaction
import warmhouse.telemetry.models.db.TelemetryData
import warmhouse.telemetry.models.schemas.TelemetryEvent
import warmhouse.telemetry.models.schemas.TelemetryRecord

object TelemetryService {
    fun save(event: TelemetryEvent): TelemetryRecord = transaction {
        val recordedAt = event.recordedAt ?: Clock.System.now()
        val id = TelemetryData.insertAndGetId {
            it[deviceId] = event.deviceId
            it[value] = event.value
            it[unit] = event.unit
            it[TelemetryData.recordedAt] = recordedAt
        }
        TelemetryRecord(id.value, event.deviceId, event.value, event.unit, recordedAt)
    }

    fun latest(deviceId: Long): TelemetryRecord? = transaction {
        TelemetryData.selectAll()
            .where { TelemetryData.deviceId eq deviceId }
            .orderBy(TelemetryData.recordedAt, SortOrder.DESC)
            .limit(1)
            .map(::toRecord)
            .firstOrNull()
    }

    fun history(deviceId: Long, from: Instant, to: Instant, limit: Int): List<TelemetryRecord> = transaction {
        TelemetryData.selectAll()
            .where {
                (TelemetryData.deviceId eq deviceId) and
                    (TelemetryData.recordedAt greaterEq from) and
                    (TelemetryData.recordedAt less to)
            }
            .orderBy(TelemetryData.recordedAt, SortOrder.ASC)
            .limit(limit)
            .map(::toRecord)
    }

    private fun toRecord(row: ResultRow): TelemetryRecord = TelemetryRecord(
        id = row[TelemetryData.id].value,
        deviceId = row[TelemetryData.deviceId],
        value = row[TelemetryData.value],
        unit = row[TelemetryData.unit],
        recordedAt = row[TelemetryData.recordedAt],
    )
}
