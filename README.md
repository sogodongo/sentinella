# Sentinella

**Sovereign AI governance control plane for production AI systems.**

Sentinella provides policy enforcement, immutable audit logging, model evaluation, and compliance instrumentation for teams operating AI in regulated or high-stakes environments. It is aligned with the EU AI Act, OWASP ASI Top 10, OpenTelemetry GenAI semantic conventions, and CycloneDX ML-BOM specification.

---

## Architecture

```
                        ┌─────────────────────────────────────────┐
                        │            Operator Console              │
                        │         (Next.js · Port 3000)           │
                        └──────────────────┬──────────────────────┘
                                           │
                        ┌──────────────────▼──────────────────────┐
                        │               Gateway                    │
                        │     AI traffic proxy · Port 8080         │
                        │   rate limiting · auth · trace inject    │
                        └────┬──────────────┬───────────────┬─────┘
                             │              │               │
               ┌─────────────▼──┐   ┌───────▼──────┐  ┌───▼──────────┐
               │     Policy     │   │    Ledger    │  │    Evals     │
               │   Port 8081    │   │  Port 8082   │  │  Port 8083   │
               │ OPA evaluation │   │  audit trail │  │ model evals  │
               └───────┬────────┘   └──────┬───────┘  └──────┬───────┘
                       │                   │                  │
               ┌───────▼────────┐   ┌──────▼───────┐  ┌──────▼───────┐
               │      OPA       │   │   Postgres   │  │    Kafka     │
               │   Port 8181    │   │  Port 5432   │  │  Port 9092   │
               └────────────────┘   └──────────────┘  └──────────────┘

                        ┌──────────────────────────────────────────┐
                        │               AI-BOM Service             │
                        │     CycloneDX ML-BOM · Port 8084         │
                        └──────────────────────────────────────────┘

  Observability: OpenTelemetry → Jaeger (traces) · Prometheus (metrics) · Grafana (dashboards)
  Object Store:  MinIO (Iceberg tables, BOM artifacts, eval results)
```

---

## Services

| Service   | Language             | Port | Responsibility |
|-----------|----------------------|------|----------------|
| gateway   | Go                   | 8080 | AI traffic proxy, rate limiting, auth, trace injection |
| policy    | Python / FastAPI     | 8081 | OPA-backed policy evaluation, EU AI Act rule engine |
| ledger    | Python / FastAPI     | 8082 | Immutable audit trail, Iceberg-backed event log |
| evals     | Python / FastAPI     | 8083 | Model evaluation engine, quality and safety scoring |
| aibom     | Python / FastAPI     | 8084 | CycloneDX ML-BOM generation and artifact management |
| console   | TypeScript / Next.js | 3000 | Operator UI, compliance dashboards, policy management |

---

## Compliance Mapping

| Standard              | Coverage |
|-----------------------|----------|
| EU AI Act (2024)      | Risk classification · transparency logging · human oversight hooks |
| OWASP ASI Top 10      | Prompt injection defense · model access control · audit requirements |
| NIST AI RMF           | Govern · Map · Measure · Manage lifecycle instrumentation |
| CycloneDX ML-BOM      | Model provenance · dependency tracking · artifact signing |
| OpenTelemetry GenAI   | Standardized AI span attributes · token usage · model metadata |

---

## Quickstart

**Prerequisites:** Docker, Docker Compose, Go 1.22+, Python 3.11+, Node.js 20+

```bash
git clone git@github.com:sogodongo/sentinella.git
cd sentinella
cp .env.example .env.local
make dev
```

Services will be available at:

| Interface      | URL |
|----------------|-----|
| Console UI     | http://localhost:3000 |
| Gateway API    | http://localhost:8080 |
| Jaeger Traces  | http://localhost:16686 |
| Grafana        | http://localhost:3001 |
| MinIO Console  | http://localhost:9001 |

---

## Repository Structure

```
sentinella/
├── services/        # Runtime services (gateway, policy, ledger, evals, aibom, console)
├── policies/        # OPA Rego policy bundles
├── infra/           # Terraform, Helm charts, Prometheus config
├── schemas/         # OpenAPI contracts, shared type definitions
├── docs/            # ADRs, architecture diagrams, runbooks
└── examples/        # Quickstart and integration examples
```

---

## Development

```bash
make help               # Show all available targets
make dev                # Start full stack locally
make test               # Run all service tests
make lint               # Run all linters
make fmt                # Format all code
make validate-policies  # Validate OPA Rego bundles
```

---

## Architecture Decisions

Significant engineering decisions are documented as ADRs in [`docs/adr/`](docs/adr/).

| ADR | Decision |
|-----|----------|
| [0001](docs/adr/0001-monorepo-structure.md) | Monorepo structure |
| [0002](docs/adr/0002-language-selection.md) | Language selection per service |

---

## Observability

Sentinella emits OpenTelemetry traces, Prometheus metrics, and structured JSON logs from every service. The local development stack includes Jaeger for trace visualization and Grafana for metrics dashboards.

All AI inference events passing through the gateway are instrumented with OpenTelemetry GenAI semantic conventions — model name, token counts, latency, and policy decision outcome are captured on every span.

---

## Security Posture

- All inter-service communication is authenticated in production (mTLS via service mesh)
- Policy decisions are made by OPA — no inline business logic encodes compliance rules
- The audit ledger is append-only; no service has delete access to ledger records
- Secrets are never committed; `.env.example` documents required variables without values
- All container images run as non-root

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
