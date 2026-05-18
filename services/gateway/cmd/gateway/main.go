package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/sogodongo/sentinella/services/gateway/internal/config"
	"github.com/sogodongo/sentinella/services/gateway/internal/handler"
	"github.com/sogodongo/sentinella/services/gateway/internal/health"
	"github.com/sogodongo/sentinella/services/gateway/internal/middleware"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))

	cfg, err := config.Load()
	if err != nil {
		logger.Error("failed to load config", "error", err)
		os.Exit(1)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	shutdownTracer, err := middleware.InitTracer(ctx, cfg.Telemetry.OTLPEndpoint, cfg.Telemetry.ServiceName)
	if err != nil {
		logger.Warn("failed to init tracer, continuing without tracing", "error", err)
	} else {
		defer func() {
			shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 5*time.Second)
			defer shutdownCancel()
			if err := shutdownTracer(shutdownCtx); err != nil {
				logger.Error("tracer shutdown error", "error", err)
			}
		}()
	}

	mux := http.NewServeMux()

	mux.HandleFunc("/healthz", health.Liveness(cfg.Telemetry.ServiceName))
	mux.HandleFunc("/readyz", health.Readiness(cfg.Telemetry.ServiceName))
	mux.Handle("/metrics", promhttp.Handler())

	proxy := handler.NewProxyHandler(
		cfg.Upstream.PolicyServiceURL,
		cfg.Upstream.LedgerServiceURL,
		logger,
	)

	chain := middleware.Telemetry(cfg.Telemetry.ServiceName)(
		middleware.RateLimit(cfg.RateLimit.RequestsPerSecond, cfg.RateLimit.BurstSize)(
			middleware.Auth(cfg.Auth.Disabled, cfg.Auth.StaticTokens)(
				proxy,
			),
		),
	)

	mux.Handle("/v1/", chain)

	srv := &http.Server{
		Addr:         fmt.Sprintf(":%s", cfg.HTTP.Port),
		Handler:      mux,
		ReadTimeout:  cfg.HTTP.ReadTimeout,
		WriteTimeout: cfg.HTTP.WriteTimeout,
		IdleTimeout:  cfg.HTTP.IdleTimeout,
		ErrorLog:     slog.NewLogLogger(logger.Handler(), slog.LevelError),
	}

	go func() {
		logger.Info("gateway starting",
			"port", cfg.HTTP.Port,
			"env", cfg.Env,
		)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Error("server error", "error", err)
			os.Exit(1)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("gateway shutting down")
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer shutdownCancel()

	if err := srv.Shutdown(shutdownCtx); err != nil {
		logger.Error("graceful shutdown failed", "error", err)
		os.Exit(1)
	}

	logger.Info("gateway stopped")
}
