import { ArrowLeft, ShoppingBag } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'

import { ChannelBadge, OrderStatusBadge } from '../components/Badge'
import { Panel } from '../components/Panel'
import { Button } from '../components/Button'
import { Skeleton } from '../components/Skeleton'
import { ErrorState } from '../components/ErrorState'
import { EmptyState } from '../components/EmptyState'
import { ApiError } from '../lib/api'
import { useOrderDetail } from '../features/orders/api'
import { formatVND, formatDateTime } from '../utils'

export function OrderDetailPage() {

  const { orderId } = useParams<{ orderId: string }>()
  const navigate = useNavigate()
  const numericId = orderId ? parseInt(orderId, 10) : null

  const { data: order, isLoading, error, refetch } = useOrderDetail(numericId)

  if (isLoading) {
    return (
      <div className="p-6 max-w-[900px] w-full space-y-4">
        <Skeleton className="h-8 w-32 rounded-md" />
        <Skeleton className="h-16 w-full rounded-xl" />
        <Skeleton className="h-40 w-full rounded-xl" />
        <Skeleton className="h-32 w-full rounded-xl" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 max-w-[900px] w-full">
        <Button
          variant="ghost"
          size="sm"
          icon={<ArrowLeft className="w-3.5 h-3.5" />}
          onClick={() => {
            void navigate('/orders')
          }}
          className="mb-4"
        >
          Back to Orders
        </Button>
        <ErrorState
          title="Failed to load order detail"
          message={error.message}
          requestId={error instanceof ApiError ? error.requestId : undefined}
          onRetry={() => {
            void refetch()
          }}
        />
      </div>
    )
  }

  if (!order) {
    return (
      <div className="p-6 max-w-[900px] w-full">
        <Button
          variant="ghost"
          size="sm"
          icon={<ArrowLeft className="w-3.5 h-3.5" />}
          onClick={() => {
            void navigate('/orders')
          }}
          className="mb-4"
        >
          Back to Orders
        </Button>
        <EmptyState
          icon={ShoppingBag}
          title="Order not found"
          description={`Order #${orderId ?? ''} does not exist in the database.`}
        />
      </div>
    )
  }

  const revenue = order.total_amount
  const cogs = order.items.reduce((sum, item) => sum + item.unit_cost * item.quantity, 0)
  const grossProfit = revenue - cogs
  const profitMargin = revenue > 0 ? ((grossProfit / revenue) * 100).toFixed(1) : '0.0'

  return (
    <div className="p-6 max-w-[900px] w-full">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => {
            void navigate('/orders')
          }}
          className="flex items-center gap-1.5 text-sm text-text-secondary hover:text-gray-700 transition-colors mb-4 focus-visible:outline-none cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Orders
        </button>
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-2xl font-bold text-gray-900">Order #{order.id}</h1>
              <OrderStatusBadge status={order.status} />
            </div>
            <p className="text-sm text-text-secondary mt-1">
              External ID: <span className="font-mono-data font-medium text-gray-800">{order.external_order_id}</span>
            </p>
          </div>
        </div>
      </div>

      {/* Order Header Summary */}
      <Panel className="mb-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-text-secondary mb-1">Channel</p>
            <ChannelBadge channel={order.channel} />
          </div>

          <div>
            <p className="text-xs text-text-secondary mb-1">Order Date</p>
            <p className="text-sm font-medium text-gray-800">{formatDateTime(order.order_date)}</p>
          </div>
          <div>
            <p className="text-xs text-text-secondary mb-1">Status</p>
            <OrderStatusBadge status={order.status} />
          </div>
          <div>
            <p className="text-xs text-text-secondary mb-1">Total Amount</p>
            <p className="text-sm font-bold tabular-nums text-gray-900">{formatVND(order.total_amount)}</p>
          </div>
        </div>
      </Panel>


      {/* Order Items Table */}
      <Panel title="Order Line Items" className="mb-4" noPadding>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-gray-50">
                <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  SKU
                </th>
                <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Product Name
                </th>
                <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Qty
                </th>
                <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Unit Price
                </th>
                <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Unit Cost
                </th>
                <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Line Total
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {order.items.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3.5">
                    <span className="font-mono-data text-sm font-medium text-gray-800">
                      {item.sku ?? `Product #${item.product_id}`}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="text-sm text-gray-700">{item.product_name ?? '—'}</span>
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <span className="text-sm tabular-nums text-gray-700">{item.quantity}</span>
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <span className="text-sm tabular-nums text-gray-700">{formatVND(item.unit_price)}</span>
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <span className="text-sm tabular-nums text-gray-700">{formatVND(item.unit_cost)}</span>
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <span className="text-sm font-medium tabular-nums text-gray-800">
                      {formatVND(item.unit_price * item.quantity)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {/* Financial Summary */}
      <Panel title="Financial Summary">
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-sm text-gray-600">Revenue</span>
            <span className="text-sm font-medium tabular-nums text-gray-800">{formatVND(revenue)}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-sm text-gray-600">Cost of Goods Sold (COGS)</span>
            <span className="text-sm font-medium tabular-nums text-gray-800">{formatVND(cogs)}</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <div>
              <span className="text-sm font-semibold text-gray-800">Gross Profit</span>
              <span className="text-xs text-text-secondary ml-2">({profitMargin}% margin)</span>
            </div>
            <span
              className={`text-base font-bold tabular-nums ${
                grossProfit >= 0 ? 'text-success-700' : 'text-critical-600'
              }`}
            >
              {formatVND(grossProfit)}
            </span>
          </div>
        </div>
      </Panel>
    </div>
  )
}
