package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
)

// TemperatureResponse matches the contract expected by the smart_home app
type TemperatureResponse struct {
	Value       float64   `json:"value"`
	Unit        string    `json:"unit"`
	Timestamp   time.Time `json:"timestamp"`
	Location    string    `json:"location"`
	Status      string    `json:"status"`
	SensorID    string    `json:"sensor_id"`
	SensorType  string    `json:"sensor_type"`
	Description string    `json:"description"`
}

func main() {
	router := gin.Default()

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "ok",
		})
	})

	// GET /temperature?location=Living+Room&sensorId=1
	router.GET("/temperature", func(c *gin.Context) {
		location := c.Query("location")
		sensorID := c.Query("sensorId")
		c.JSON(http.StatusOK, buildTemperature(location, sensorID))
	})

	// GET /temperature/{sensorId}
	router.GET("/temperature/:sensorId", func(c *gin.Context) {
		c.JSON(http.StatusOK, buildTemperature("", c.Param("sensorId")))
	})

	addr := getEnv("PORT", ":8081")
	log.Printf("temperature-api listening on %s\n", addr)
	if err := router.Run(addr); err != nil {
		log.Fatalf("Failed to start server: %v\n", err)
	}
}

// buildTemperature returns a simulated sensor reading
func buildTemperature(location, sensorID string) TemperatureResponse {
	// If no location is provided, use a default based on sensor ID
	if location == "" {
		switch sensorID {
		case "1":
			location = "Living Room"
		case "2":
			location = "Bedroom"
		case "3":
			location = "Kitchen"
		default:
			location = "Unknown"
		}
	}

	// If no sensor ID is provided, generate one based on location
	if sensorID == "" {
		switch location {
		case "Living Room":
			sensorID = "1"
		case "Bedroom":
			sensorID = "2"
		case "Kitchen":
			sensorID = "3"
		default:
			sensorID = "0"
		}
	}

	return TemperatureResponse{
		Value:       randomTemperature(),
		Unit:        "°C",
		Timestamp:   time.Now().UTC(),
		Location:    location,
		Status:      "active",
		SensorID:    sensorID,
		SensorType:  "temperature",
		Description: fmt.Sprintf("Simulated temperature sensor in %s", location),
	}
}

// randomTemperature returns a value between 15.0 and 30.0 with one decimal
func randomTemperature() float64 {
	return float64(150+rand.Intn(151)) / 10
}

// getEnv gets an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}
