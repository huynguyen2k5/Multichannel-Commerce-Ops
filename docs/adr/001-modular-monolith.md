# ADR-001: Use a modular monolith for the backend

- Status: Accepted
- Date: 2026-09-03

## Context

MCO is a portfolio-scale internal operations system with one team, one transactional database, and tightly coupled order/inventory/ledger consistency requirements. Splitting these capabilities into network services would add deployment, observability, failure, and distributed-transaction costs without a current scaling or ownership need.

## Decision

Use one FastAPI deployable organized by business module. Inside each module the dependency direction is `router -> service -> repository -> model`. Cross-domain writes go through services. Reports may perform read-only cross-domain SQL aggregation.

## Consequences

- One ACID transaction can protect critical order processing.
- Modules remain independently understandable without introducing network boundaries.
- A future extraction is possible if scale/team ownership creates evidence for it, but is not pre-designed now.

## Rejected

Microservices, event bus, CQRS, and service mesh are rejected for V1 because they solve constraints MCO does not currently have.
