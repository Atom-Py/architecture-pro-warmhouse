package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"smarthome/db"
	"smarthome/handlers"
	"smarthome/kafka"
	"smarthome/services"

	"github.com/gin-gonic/gin"
)

func main() {
	// Set up database connection
	dbURL := getEnv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/smarthome")
	database, err := db.New(dbURL)
	if err != nil {
		log.Fatalf("Unable to connect to database: %v\n", err)
	}
	defer database.Close()

	log.Println("Connected to database successfully")

	// Initialize temperature service
	temperatureAPIURL := getEnv("TEMPERATURE_API_URL", "http://temperature-api:8081")
	temperatureService := services.NewTemperatureService(temperatureAPIURL)
	log.Printf("Temperature service initialized with API URL: %s\n", temperatureAPIURL)

	// Initialize kafka client (nil when KAFKA_BOOTSTRAP_SERVERS is not set, all publishing becomes no-op)
	kafkaClient := kafka.New(getEnv("KAFKA_BOOTSTRAP_SERVERS", ""))
	defer kafkaClient.Close()

	// Consume device commands from the device service and execute them on sensors
	consumerCtx, stopConsumer := context.WithCancel(context.Background())
	defer stopConsumer()
	go kafkaClient.ConsumeCommands(consumerCtx, makeCommandHandler(database, kafkaClient))

	// Initialize router
	router := gin.Default()

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "ok",
		})
	})

	// API routes
	apiRoutes := router.Group("/api/v1")

	// Register sensor routes
	sensorHandler := handlers.NewSensorHandler(database, temperatureService, kafkaClient)
	sensorHandler.RegisterRoutes(apiRoutes)

	// Start server
	srv := &http.Server{
		Addr:    getEnv("PORT", ":8080"),
		Handler: router,
	}

	// Start the server in a goroutine
	go func() {
		log.Printf("Server starting on %s\n", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v\n", err)
		}
	}()

	// Wait for interrupt signal to gracefully shut down the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	// Create a deadline for server shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v\n", err)
	}

	log.Println("Server exited properly")
}

// makeCommandHandler executes device commands on monolith sensors and publishes confirmations.
// The monolith acts as a temporary device gateway during the transition period.
func makeCommandHandler(database *db.DB, kafkaClient *kafka.Client) func(kafka.DeviceCommandEvent) {
	return func(event kafka.DeviceCommandEvent) {
		if event.SensorID == nil {
			log.Printf("Command %s for device %d has no sensor binding, skipping", event.CommandID, event.DeviceID)
			return
		}

		var sensorStatus, deviceStatus string
		switch event.Command {
		case "turn_on":
			sensorStatus, deviceStatus = "active", "on"
		case "turn_off":
			sensorStatus, deviceStatus = "inactive", "off"
		default:
			log.Printf("Command %s '%s' is not supported by the monolith executor", event.CommandID, event.Command)
			return
		}

		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		sensor, err := database.GetSensorByID(ctx, *event.SensorID)
		if err != nil {
			log.Printf("Command %s: sensor %d not found: %v", event.CommandID, *event.SensorID, err)
			return
		}
		if err := database.UpdateSensorValue(ctx, sensor.ID, sensor.Value, sensorStatus); err != nil {
			log.Printf("Command %s: failed to update sensor %d: %v", event.CommandID, sensor.ID, err)
			return
		}
		log.Printf("Command %s executed: sensor %d -> %s", event.CommandID, sensor.ID, sensorStatus)

		if err := kafkaClient.PublishDeviceStatus(ctx, kafka.DeviceStatusEvent{
			DeviceID:   event.DeviceID,
			Status:     deviceStatus,
			CommandID:  event.CommandID,
			OccurredAt: time.Now().UTC(),
		}); err != nil {
			log.Printf("Command %s: failed to publish device status: %v", event.CommandID, err)
		}
	}
}

// getEnv gets an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}
