# ADR-0002: Language Selection Per Service

**Status:** Accepted
**Date:** 2026-05-19
**Deciders:** Platform Engineering

## Context

Sentinella comprises six services with different runtime characteristics, team skill profiles, and ecosystem requirements. A uniform language choice would sacrifice fitness-for-purpose; pure polyglotism without reasoning would create maintenance overhead.

## Decisions

| Service  | Language           | Rationale |
|----------|--------------------|-----------|
| gateway  | Go                 | Low-latency request interception, high concurrency, small binary, native gRPC/HTTP2 support. |
| policy   | Python             | OPA Python SDK and policy-as-code ecosystem are Python-native. FastAPI provides typed contract enforcement. |
| ledger   | Python             | Iceberg and Delta Lake SDKs most mature in Python. Audit trail writes are not latency-sensitive. |
| evals    | Python             | ML evaluation libraries (deepeval, ragas) are Python-first. |
| aibom    | Python             | CycloneDX Python SDK is the reference implementation. Batch workload, not a hot path. |
| console  | TypeScript/Next.js | Operator UIs require a component ecosystem and real-time capability. |

## Policy Language

Rego (OPA) for all policy definitions. The only language with native OPA toolchain support and a formal evaluation model.

## Tradeoffs

Polyglot monorepos require per-service CI configuration and per-service linting toolchains. Accepted as the cost of runtime fitness. Forcing everything into Python would require reimplementing Go concurrency in a latency-sensitive gateway — a worse tradeoff.
