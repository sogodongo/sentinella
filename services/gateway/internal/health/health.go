package health

import (
	"encoding/json"
	"net/http"
	"time"
)

type status struct {
	Status    string    `json:"status"`
	Service   string    `json:"service"`
	Timestamp time.Time `json:"timestamp"`
}

// Liveness reports whether the process is alive.
// Kubernetes uses this to decide whether to restart the container.
func Liveness(service string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(status{
			Status:    "ok",
			Service:   service,
			Timestamp: time.Now().UTC(),
		})
	}
}

// Readiness reports whether the service is ready to accept traffic.
// Extend this to check upstream dependency connectivity.
func Readiness(service string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(status{
			Status:    "ready",
			Service:   service,
			Timestamp: time.Now().UTC(),
		})
	}
}
