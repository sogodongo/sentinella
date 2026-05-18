package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

type Config struct {
	Env  string
	HTTP HTTPConfig
	Auth AuthConfig
	Upstream UpstreamConfig
	Telemetry TelemetryConfig
	RateLimit RateLimitConfig
}

type HTTPConfig struct {
	Port         string
	ReadTimeout  time.Duration
	WriteTimeout time.Duration
	IdleTimeout  time.Duration
}

type AuthConfig struct {
	// In development, auth is bypassed with a static token.
	// In production this resolves against an identity provider.
	StaticTokens []string
	Disabled     bool
}

type UpstreamConfig struct {
	PolicyServiceURL string
	LedgerServiceURL string
}

type TelemetryConfig struct {
	OTLPEndpoint string
	ServiceName  string
}

type RateLimitConfig struct {
	RequestsPerSecond float64
	BurstSize         int
}

func Load() (*Config, error) {
	rps, err := strconv.ParseFloat(env("RATE_LIMIT_RPS", "100"), 64)
	if err != nil {
		return nil, fmt.Errorf("invalid RATE_LIMIT_RPS: %w", err)
	}

	burst, err := strconv.Atoi(env("RATE_LIMIT_BURST", "200"))
	if err != nil {
		return nil, fmt.Errorf("invalid RATE_LIMIT_BURST: %w", err)
	}

	return &Config{
		Env: env("SENTINELLA_ENV", "development"),
		HTTP: HTTPConfig{
			Port:         env("GATEWAY_PORT", "8080"),
			ReadTimeout:  30 * time.Second,
			WriteTimeout: 30 * time.Second,
			IdleTimeout:  120 * time.Second,
		},
		Auth: AuthConfig{
			Disabled: env("SENTINELLA_ENV", "development") == "development",
		},
		Upstream: UpstreamConfig{
			PolicyServiceURL: env("POLICY_SERVICE_URL", "http://localhost:8081"),
			LedgerServiceURL: env("LEDGER_SERVICE_URL", "http://localhost:8082"),
		},
		Telemetry: TelemetryConfig{
			OTLPEndpoint: env("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
			ServiceName:  env("OTEL_SERVICE_NAME", "sentinella-gateway"),
		},
		RateLimit: RateLimitConfig{
			RequestsPerSecond: rps,
			BurstSize:         burst,
		},
	}, nil
}

func env(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
