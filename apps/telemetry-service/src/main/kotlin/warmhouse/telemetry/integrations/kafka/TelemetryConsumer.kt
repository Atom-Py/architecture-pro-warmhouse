package warmhouse.telemetry.integrations.kafka

import java.time.Duration
import java.util.Properties
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.concurrent.thread
import kotlinx.serialization.json.Json
import org.apache.kafka.clients.consumer.ConsumerConfig
import org.apache.kafka.clients.consumer.KafkaConsumer
import org.apache.kafka.common.serialization.StringDeserializer
import org.slf4j.LoggerFactory
import warmhouse.telemetry.config.KafkaSettings
import warmhouse.telemetry.models.schemas.TelemetryEvent
import warmhouse.telemetry.services.TelemetryService

class TelemetryConsumer(private val settings: KafkaSettings) {
    private val logger = LoggerFactory.getLogger(javaClass)
    private val running = AtomicBoolean(true)
    private val json = Json { ignoreUnknownKeys = true }

    // kafka-clients is a blocking API, so the consumer loop lives on its own thread
    fun start() {
        thread(name = "telemetry-consumer", isDaemon = true) { run() }
    }

    fun stop() {
        running.set(false)
    }

    private fun run() {
        val properties = Properties().apply {
            put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, settings.bootstrapServers)
            put(ConsumerConfig.GROUP_ID_CONFIG, settings.consumerGroup)
            put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer::class.java.name)
            put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer::class.java.name)
            put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest")
        }
        KafkaConsumer<String, String>(properties).use { consumer ->
            consumer.subscribe(listOf(settings.telemetryTopic))
            logger.info("telemetry consumer started, topic={}", settings.telemetryTopic)
            while (running.get()) {
                val records = consumer.poll(Duration.ofSeconds(1))
                for (record in records) {
                    try {
                        val event = json.decodeFromString<TelemetryEvent>(record.value())
                        TelemetryService.save(event)
                    } catch (exception: Exception) {
                        logger.error("failed to process telemetry message", exception)
                    }
                }
            }
        }
    }
}
