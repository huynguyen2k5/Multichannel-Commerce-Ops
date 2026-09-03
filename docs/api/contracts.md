# MCO HTTP API contract (V1)

Base path: `/api/v1`. Mock source endpoints intentionally live under `/mock/v1` because they simulate external channels rather than business APIs.

## System

### `GET /health`

Liveness only. Returns `200 {"status":"ok"}` without checking PostgreSQL.

### `GET /ready`

Readiness. Executes `SELECT 1`; returns `200 {"status":"ready"}` or `503 {"status":"unavailable"}`.

## Order import

### `POST /api/v1/orders/import`

Canonical V1 request:

```json
{
  "channel": "shopee",
  "external_order_id": "SP-10001",
  "order_date": "2026-09-01T02:00:00Z",
  "status": "paid",
  "total_amount": "500000.00",
  "items": [
    {"sku": "TEE-BLK-M", "quantity": 2, "unit_price": "250000.00"}
  ]
}
```

Rules:

- V1 accepts only `paid` orders.
- `total_amount` must equal the exact item-line sum.
- duplicate SKU lines in one order are rejected in V1;
- every SKU must already exist in the product catalog;
- available stock must cover the requested quantity;
- `(channel, external_order_id)` is idempotent.

New import: `201` with `{"status":"imported","order_id":123}`.

Existing import: `200` with `{"status":"duplicate","order_id":123}` and no inventory/ledger duplication.

### `GET /api/v1/orders?limit=50&offset=0`

Returns normalized orders, newest first. `limit` is `1..100`.

### `GET /api/v1/orders/{id}`

Returns an order plus item price and historical cost snapshots.

## Inventory

### `GET /api/v1/inventory`

Returns SKU, name, cost, current stock, threshold, and `is_low_stock`. Stock mutation is not exposed as a general public CRUD endpoint in V1; order processing is the owner of sale consumption.

## Reports

### `GET /api/v1/reports/daily?date=2026-09-03`

Returns daily totals and channel breakdown:

- order count;
- revenue;
- COGS;
- gross profit = revenue - COGS.

Authoritative calculations happen in FastAPI/PostgreSQL, not React.

## Alerts

### `GET /api/v1/alerts?resolved=false`

Lists active alerts by default.

### `PATCH /api/v1/alerts/{id}/resolve`

Idempotently resolves an alert and persists `resolved_at`.

### `GET /api/v1/alerts/pending-notifications`

Automation endpoint for active alerts without `notified_at`.

### `PATCH /api/v1/alerts/{id}/notified`

Idempotently persists Telegram delivery completion. n8n invokes it only after the Telegram request succeeds.

## Reconciliation

### `POST /api/v1/reconciliations`

```json
{
  "source_system": "shopee",
  "orders": [
    {"external_order_id":"SP-10001","total_amount":"500000.00"}
  ]
}
```

Checks source -> local order -> revenue -> COGS and records mismatch detail. Current mismatch codes:

- `MISSING_ORDER`
- `TOTAL_MISMATCH`
- `REVENUE_MISMATCH`
- `COGS_MISMATCH`

### `GET /api/v1/reconciliations`

Returns newest reconciliation history.

### `GET /api/v1/reconciliations/{id}`

Returns one recorded run including mismatch detail.

## Mock source endpoints

- `GET /mock/v1/shopee/orders`
- `GET /mock/v1/tiktok/orders`
- `GET /mock/v1/website/orders`

Fixtures are deterministic so tests and reconciliation are reproducible.

## Error envelope

Application and validation failures use one envelope:

```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "Insufficient stock for SKU 'TEE-BLK-M'",
    "request_id": "...",
    "details": {}
  }
}
```

`X-Request-ID` is accepted/generated and returned on responses for correlation. Unexpected exceptions return a generic `INTERNAL_ERROR`; stack traces remain server-side.

## Authentication boundary

V1 is a portfolio/demo system and does not implement end-user authentication/RBAC. Do not expose mutation endpoints to real operational data on a public network without an access-control layer (for example private networking/Cloudflare Access) or application authentication/authorization.
