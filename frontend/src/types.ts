export type Channel = "shopee" | "tiktok" | "website"
export type OrderStatus = "pending" | "processing" | "completed" | "cancelled" | "paid"
export type AlertSeverity = "critical" | "warning" | "info"
export type AlertStatus = "active" | "resolved"
export type ReconciliationStatus = "success" | "mismatch" | "failed" | "running"
export type InventoryStatus = "healthy" | "low" | "out"

export interface ChannelReport {
  channel: Channel
  channel_id?: number
  channel_code?: string
  channel_name?: string
  revenue: number
  cogs: number
  gross_profit: number
  order_count: number
}

export interface DailyReport {
  date: string
  revenue: number
  cogs: number
  gross_profit: number
  order_count: number
  channels: ChannelReport[]
}

export interface OrderItem {
  sku?: string
  product_name?: string
  quantity: number
  unit_price: number
  unit_cost: number
}

export interface Order {
  id: number
  order_id: string
  external_order_id: string
  channel: string
  order_date: string
  status: OrderStatus
  total_amount: number
  items?: OrderItem[]
}

export interface InventoryItem {
  product_id?: number
  sku: string
  product_name: string
  current_stock: number
  reorder_threshold: number
  is_low_stock?: boolean
}

export interface Alert {
  id: number
  severity: AlertSeverity
  type: string
  message: string
  created_at: string
  status: AlertStatus
}

export interface ReconciliationMismatch {
  order_id: string
  type: string
  source_value?: number
  ledger_value?: number
  difference?: number
  expected?: string | number | null
  actual?: string | number | null
  code?: string
}

export interface Reconciliation {
  id: number
  source: string
  status: ReconciliationStatus
  started_at: string
  completed_at: string | null
  records_checked: number
  mismatches_found: number
  detail?: ReconciliationMismatch[]
}

export type Page =
  | "dashboard"
  | "orders"
  | "order-detail"
  | "inventory"
  | "alerts"
  | "reconciliation"
  | "reconciliation-detail"

export interface NavState {
  page: Page
  orderId?: string
  reconciliationId?: number
}

export interface ToastItem {
  id: number
  message: string
  type: "success" | "error" | "info"
}
