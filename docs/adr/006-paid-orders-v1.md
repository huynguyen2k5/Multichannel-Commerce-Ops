# ADR-006: Process only paid orders in V1

- Status: Accepted
- Date: 2026-09-03

## Context

A full commerce order state machine would require cancellation, shipment, refund, reservation, and reversal semantics that are outside the demo objective. Allowing many statuses without defining their financial effects would create ambiguous inventory and ledger behavior.

## Decision

`OrderStatus` contains only `paid` in V1. A valid imported paid order consumes stock and records revenue/COGS in the same transaction.

## Consequences

The financial invariant is unambiguous. Refunds, cancellations, partial fulfillment, and stock reservation remain explicitly out of scope until their reversal rules are designed.
