# ADR-0001: Monorepo Structure

**Status:** Accepted
**Date:** 2026-05-19
**Deciders:** Platform Engineering

## Context

Sentinella is a multi-service AI governance platform comprising six distinct runtime services, shared policy bundles, infrastructure definitions, and a compliance-facing operator console. We needed to decide whether to manage these as separate repositories or within a single monorepo.

## Decision

We adopt a monorepo structure under `github.com/sogodongo/sentinella`, with top-level directories for services, policies, infra, schemas, and docs.

## Reasoning

Cross-service changes in a governance platform are frequent. When a schema changes in `schemas/openapi`, the gateway, ledger, and console are all affected simultaneously. In a polyrepo, this produces N pull requests, N CI runs, and coordination overhead that scales poorly. A monorepo allows atomic commits that keep the system in a consistent state.

Policy bundles in `policies/rego` are consumed by both the gateway and the policy service. Shared ownership in a single repo eliminates the version skew problem that has plagued similar projects.

## Tradeoffs

**Against:** Monorepos increase CI complexity. Build systems must be made aware of service boundaries to avoid rebuilding everything on every commit. We accept this cost and will address it with path-scoped GitHub Actions triggers as CI matures.

**Against:** Go module isolation requires each service to maintain its own `go.mod`. This is standard practice in Go monorepos.

## Alternatives Considered

- **Polyrepo:** Rejected. Cross-service coordination cost is too high for a platform where correctness across service boundaries is a compliance requirement.
- **Nx / Turborepo:** Considered for the TypeScript console only. Deferred — premature optimization at this stage.
