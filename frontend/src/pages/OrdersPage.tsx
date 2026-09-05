import { useState } from 'react'
import { ShoppingBag, Search, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { PageHeader } from '../components/PageHeader'
import { OrderStatusBadge, ChannelBadge } from '../components/Badge'
import { EmptyState } from '../components/EmptyState'
import { TableRowSkeleton } from '../components/Skeleton'
import { ErrorState } from '../components/ErrorState'
import { ApiError } from '../lib/api'
import { useOrders } from '../features/orders/api'
import { formatVND, formatDateTime } from '../utils'
import type { Channel } from '../types'

const CHANNELS: { value: Channel | 'all'; label: string }[] = [
  { value: 'all', label: 'All channels' },
  { value: 'shopee', label: 'Shopee' },
  { value: 'tiktok', label: 'TikTok Shop' },
  { value: 'website', label: 'Website' },
]

export function OrdersPage() {
  const navigate = useNavigate()
  const [channelFilter, setChannelFilter] = useState<Channel | 'all'>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')

  const { data: orders, isLoading, error, refetch } = useOrders({
    channel: channelFilter !== 'all' ? channelFilter : undefined,
    status: statusFilter !== 'all' ? statusFilter : undefined,
    search: searchQuery || undefined,
  })

  const hasActiveFilters = channelFilter !== 'all' || statusFilter !== 'all' || searchQuery.trim() !== ''

  const clearFilters = () => {
    setChannelFilter('all')
    setStatusFilter('all')
    setSearchQuery('')
  }

  return (
    <div className="p-6 max-w-[1440px] w-full">
      <PageHeader
        title="Orders"
        subtitle="Normalized orders imported from connected commerce channels."
      />

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center gap-3 mb-5">
        <div className="relative min-w-[220px]">
          <Search className="w-4 h-4 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search external order ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8 pl-8 pr-3 text-sm border border-border rounded-lg bg-white text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-600 w-full"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <select
          value={channelFilter}
          onChange={(e) => setChannelFilter(e.target.value as Channel | 'all')}
          className="h-8 px-3 text-sm border border-border rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-600 cursor-pointer"
        >
          {CHANNELS.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="h-8 px-3 text-sm border border-border rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-600 cursor-pointer"
        >
          <option value="all">All statuses</option>
          <option value="paid">Paid</option>
        </select>

        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-xs text-primary-600 hover:text-primary-700 font-medium focus-visible:outline-none cursor-pointer"
          >
            Clear filters
          </button>
        )}

        <span className="ml-auto text-xs text-text-secondary">
          {orders ? `${orders.length} orders` : 'Loading...'}
        </span>
      </div>

      {error ? (
        <ErrorState
          title="Failed to load orders"
          message={error.message}
          requestId={error instanceof ApiError ? error.requestId : undefined}
          onRetry={() => {
            void refetch()
          }}
        />
      ) : (
        /* Table */
        <div className="bg-white border border-border rounded-[10px] overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px]">
              <thead>
                <tr className="border-b border-border bg-gray-50">
                  <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Internal ID
                  </th>
                  <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    External ID
                  </th>
                  <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Channel
                  </th>
                  <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Order Date
                  </th>
                  <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Status
                  </th>
                  <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {isLoading ? (
                  Array.from({ length: 8 }).map((_, i) => <TableRowSkeleton key={i} cols={6} />)
                ) : !orders || orders.length === 0 ? (
                  <tr>
                    <td colSpan={6}>
                      <EmptyState
                        icon={ShoppingBag}
                        title="No orders found."
                        description="Try adjusting the channel filter or search keyword."
                      />
                    </td>
                  </tr>
                ) : (
                  orders.map((order) => (
                    <tr
                      key={order.id}
                      onClick={() => {
                        void navigate(`/orders/${order.id}`)
                      }}
                      className="table-row-hover hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="px-4 py-3.5">
                        <span className="font-mono-data text-sm text-gray-800">#{order.id}</span>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="font-mono-data text-sm font-medium text-gray-900">
                          {order.external_order_id}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <ChannelBadge channel={order.channel as Channel} />
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="text-sm text-gray-700">{formatDateTime(order.order_date)}</span>
                      </td>
                      <td className="px-4 py-3.5">
                        <OrderStatusBadge status={order.status} />
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span className="text-sm font-semibold tabular-nums text-gray-900">
                          {formatVND(order.total_amount)}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  )
}
