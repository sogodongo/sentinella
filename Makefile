.DEFAULT_GOAL := help

.PHONY: help
help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

.PHONY: dev
dev: ## Start all services locally via docker-compose
	docker compose up --build

.PHONY: dev-down
dev-down: ## Stop local services
	docker compose down --volumes

.PHONY: lint
lint: ## Run all linters across the monorepo
	@echo "→ gateway (Go)"
	cd services/gateway && go vet ./...
	@echo "→ policy/ledger/evals/aibom (Python)"
	cd services/policy && ruff check .
	cd services/ledger && ruff check .
	cd services/evals && ruff check .
	cd services/aibom && ruff check .
	@echo "→ console (TypeScript)"
	cd services/console && npm run lint

.PHONY: test
test: ## Run all service tests
	@echo "→ gateway"
	cd services/gateway && go test ./... -race -cover
	@echo "→ policy"
	cd services/policy && pytest -q
	@echo "→ ledger"
	cd services/ledger && pytest -q
	@echo "→ evals"
	cd services/evals && pytest -q
	@echo "→ aibom"
	cd services/aibom && pytest -q

.PHONY: fmt
fmt: ## Format all code
	cd services/gateway && gofmt -w .
	cd services/policy && ruff format .
	cd services/ledger && ruff format .
	cd services/evals && ruff format .
	cd services/aibom && ruff format .

.PHONY: validate-policies
validate-policies: ## Validate OPA Rego policies
	opa check policies/rego/

.PHONY: docs
docs: ## List ADRs
	@ls -1 docs/adr/*.md 2>/dev/null | sed 's/docs\/adr\///' || echo "No ADRs yet"
