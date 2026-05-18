package handler

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
)

var tracer = otel.Tracer("sentinella/gateway/proxy")

type InferenceRequest struct {
	Model    string         `json:"model"`
	Messages []Message      `json:"messages"`
	Metadata map[string]any `json:"metadata,omitempty"`
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ProxyHandler struct {
	policyURL string
	ledgerURL string
	client    *http.Client
	logger    *slog.Logger
}

func NewProxyHandler(policyURL, ledgerURL string, logger *slog.Logger) *ProxyHandler {
	return &ProxyHandler{
		policyURL: policyURL,
		ledgerURL: ledgerURL,
		client: &http.Client{
			Timeout: 10 * time.Second,
		},
		logger: logger,
	}
}

func (h *ProxyHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	ctx, span := tracer.Start(r.Context(), "gateway.proxy")
	defer span.End()

	body, err := io.ReadAll(io.LimitReader(r.Body, 1<<20))
	if err != nil {
		h.logger.ErrorContext(ctx, "failed to read request body", "error", err)
		httpError(w, "failed to read request", http.StatusBadRequest)
		return
	}

	var req InferenceRequest
	if err := json.Unmarshal(body, &req); err != nil {
		h.logger.ErrorContext(ctx, "invalid request payload", "error", err)
		httpError(w, "invalid request payload", http.StatusBadRequest)
		return
	}

	span.SetAttributes(
		attribute.String("ai.model", req.Model),
		attribute.Int("ai.message_count", len(req.Messages)),
	)

	allowed, reason, err := h.evaluatePolicy(ctx, req)
	if err != nil {
		h.logger.ErrorContext(ctx, "policy evaluation failed", "error", err)
		httpError(w, "policy evaluation unavailable", http.StatusServiceUnavailable)
		return
	}

	span.SetAttributes(
		attribute.Bool("sentinella.policy.allowed", allowed),
		attribute.String("sentinella.policy.reason", reason),
	)

	if !allowed {
		h.logger.InfoContext(ctx, "request blocked by policy",
			"model", req.Model,
			"reason", reason,
		)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusForbidden)
		json.NewEncoder(w).Encode(map[string]string{
			"error":  "request blocked by governance policy",
			"reason": reason,
			"code":   "POLICY_DENIED",
		})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]any{
		"id":      fmt.Sprintf("sentinel-%d", time.Now().UnixNano()),
		"model":   req.Model,
		"allowed": true,
		"message": "request accepted by Sentinella gateway",
	})
}

func (h *ProxyHandler) evaluatePolicy(ctx context.Context, req InferenceRequest) (bool, string, error) {
	payload, err := json.Marshal(map[string]any{
		"input": map[string]any{
			"model":    req.Model,
			"messages": req.Messages,
		},
	})
	if err != nil {
		return false, "", fmt.Errorf("failed to marshal policy input: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost,
		h.policyURL+"/v1/evaluate", bytes.NewReader(payload))
	if err != nil {
		return false, "", fmt.Errorf("failed to build policy request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := h.client.Do(httpReq)
	if err != nil {
		h.logger.WarnContext(ctx, "policy service unreachable, failing open", "error", err)
		return true, "policy_service_unavailable", nil
	}
	defer resp.Body.Close()

	var result struct {
		Allowed bool   `json:"allowed"`
		Reason  string `json:"reason"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return false, "", fmt.Errorf("failed to decode policy response: %w", err)
	}

	return result.Allowed, result.Reason, nil
}

func httpError(w http.ResponseWriter, msg string, code int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(map[string]string{"error": msg})
}
