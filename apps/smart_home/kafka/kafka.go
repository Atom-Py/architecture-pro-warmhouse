package kafka

import (
	"context"
	"encoding/json"
	"log"
	"time"

	segmentio "github.com/segmentio/kafka-go"
)

const (
	TelemetryTopic    = "telemetry"
	CommandsTopic     = "device-commands"
	DeviceStatusTopic = "device-status"
)

// TelemetryEvent is a sensor reading published to the telemetry topic.
// DeviceID carries the monolith sensor id during the transition period.
type TelemetryEvent struct {
	DeviceID   int       `json:"device_id"`
	Value      float64   `json:"value"`
	Unit       string    `json:"unit"`
	RecordedAt time.Time `json:"recorded_at"`
}

// DeviceCommandEvent is a command consumed from the device-commands topic
type DeviceCommandEvent struct {
	CommandID string          `json:"command_id"`
	DeviceID  int64           `json:"device_id"`
	SensorID  *int            `json:"sensor_id"`
	Command   string          `json:"command"`
	Payload   json.RawMessage `json:"payload"`
}

// DeviceStatusEvent is a command confirmation published to the device-status topic
type DeviceStatusEvent struct {
	DeviceID   int64     `json:"device_id"`
	Status     string    `json:"status"`
	CommandID  string    `json:"command_id,omitempty"`
	OccurredAt time.Time `json:"occurred_at"`
}

// Client wraps kafka producers and the command consumer.
// A nil *Client is valid: every method becomes a no-op, so the monolith
// keeps working when KAFKA_BOOTSTRAP_SERVERS is not configured.
type Client struct {
	brokers         []string
	telemetryWriter *segmentio.Writer
	statusWriter    *segmentio.Writer
}

// New creates a kafka client, or nil when brokers is empty
func New(brokers string) *Client {
	if brokers == "" {
		return nil
	}
	return &Client{
		brokers:         []string{brokers},
		telemetryWriter: newWriter(brokers, TelemetryTopic),
		statusWriter:    newWriter(brokers, DeviceStatusTopic),
	}
}

func newWriter(brokers, topic string) *segmentio.Writer {
	return &segmentio.Writer{
		Addr:                   segmentio.TCP(brokers),
		Topic:                  topic,
		Balancer:               &segmentio.LeastBytes{},
		AllowAutoTopicCreation: true,
	}
}

// Close closes the producers
func (c *Client) Close() {
	if c == nil {
		return
	}
	c.telemetryWriter.Close()
	c.statusWriter.Close()
}

// PublishTelemetryAsync publishes a sensor reading without blocking the caller
func (c *Client) PublishTelemetryAsync(sensorID int, value float64, unit string, recordedAt time.Time) {
	if c == nil {
		return
	}
	go func() {
		event := TelemetryEvent{
			DeviceID:   sensorID,
			Value:      value,
			Unit:       unit,
			RecordedAt: recordedAt,
		}
		if err := c.publish(c.telemetryWriter, event); err != nil {
			log.Printf("failed to publish telemetry for sensor %d: %v", sensorID, err)
		}
	}()
}

// PublishDeviceStatus publishes a command confirmation
func (c *Client) PublishDeviceStatus(ctx context.Context, event DeviceStatusEvent) error {
	if c == nil {
		return nil
	}
	return c.publishCtx(ctx, c.statusWriter, event)
}

func (c *Client) publish(writer *segmentio.Writer, event interface{}) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	return c.publishCtx(ctx, writer, event)
}

func (c *Client) publishCtx(ctx context.Context, writer *segmentio.Writer, event interface{}) error {
	value, err := json.Marshal(event)
	if err != nil {
		return err
	}
	return writer.WriteMessages(ctx, segmentio.Message{Value: value})
}

// ConsumeCommands reads the device-commands topic and calls handler for every command.
// Blocks until ctx is cancelled, intended to run in a goroutine.
func (c *Client) ConsumeCommands(ctx context.Context, handler func(DeviceCommandEvent)) {
	if c == nil {
		return
	}
	reader := segmentio.NewReader(segmentio.ReaderConfig{
		Brokers:  c.brokers,
		Topic:    CommandsTopic,
		GroupID:  "smart_home",
		MinBytes: 1,
		MaxBytes: 10e6,
		// pick up partitions that appear after the consumer joins,
		// otherwise a group joined before topic creation stays empty forever
		WatchPartitionChanges: true,
		ErrorLogger:           segmentio.LoggerFunc(log.Printf),
	})
	defer reader.Close()

	log.Println("device-commands consumer started")
	for {
		message, err := reader.ReadMessage(ctx)
		if err != nil {
			if ctx.Err() != nil {
				return
			}
			log.Printf("failed to read device-commands message: %v", err)
			time.Sleep(time.Second)
			continue
		}
		var event DeviceCommandEvent
		if err := json.Unmarshal(message.Value, &event); err != nil {
			log.Printf("failed to decode device-commands message: %v", err)
			continue
		}
		handler(event)
	}
}
