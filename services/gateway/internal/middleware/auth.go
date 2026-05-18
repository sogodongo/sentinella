package middleware

import (
	"encoding/json"
	"net/http"
	"strings"
)

// Auth validates Bearer tokens on incoming requests.
// In development mode (disabled=true) all requests are allowed through.
// Production should replace this with JWT validation against an IdP.
func Auth(disabled bool, validTokens []string) func(http.Handler) http.Handler {
	tokenSet := make(map[string]struct{}, len(validTokens))
	for _, t := range validTokens {
		tokenSet[t] = struct{}{}
	}

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if disabled {
				next.ServeHTTP(w, r)
				return
			}

			header := r.Header.Get("Authorization")
			if !strings.HasPrefix(header, "Bearer ") {
				unauthorized(w, "missing or malformed Authorization header")
				return
			}

			token := strings.TrimPrefix(header, "Bearer ")
			if _, ok := tokenSet[token]; !ok {
				unauthorized(w, "invalid token")
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

func unauthorized(w http.ResponseWriter, reason string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusUnauthorized)
	json.NewEncoder(w).Encode(map[string]string{
		"error": reason,
		"code":  "UNAUTHORIZED",
	})
}
