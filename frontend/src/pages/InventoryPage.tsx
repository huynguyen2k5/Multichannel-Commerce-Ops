import { useMemo, useState } from 'react'
import { Package, Search } from 'lucide-react'

import { InventoryStatusBadge } from '../components/Badge'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { PageHeader } from '../components/PageHeader'
import { TableRowSkeleton } from '../components/Skeleton'
import { useInventory } from '../features/inventory/api'
import type { InventoryStatus } from '../types'
import { formatVND } from '../utils'

function getStatus(current: number, threshold: number): InventoryStatus {
  if (current === 0) return 'out'
  if (current <= threshold) return 'low'
  return 'healthy'
}

const STATUS_ORDER: Record<InventoryStatus, number> = { out: 0, low: 1, healthy: 2 }

const STATUS_FILTERS: Array<{ value: InventoryStatus | 'all'; label: string }> = [
  { value: 'all', label: 'All' },
  { value: 'out', label: 'Out of Stock' },
  { value: 'low', label: 'Low Stock' },
  { value: 'healthy', label: 'Healthy' },
]

export function InventoryPage() {
  const { data: inventory, isLoading, error, refetch } = useInventory()
  const [statusFilter, setStatusFilter] = useState<InventoryStatus | 'all'>('all')
  const [search, setSearch] = useState('')

  const items = useMemo(() => {
    if (!inventory) return []
    let list = [...inventory]

    if (search.trim()) {
      const q = search.trim().toLowerCase()
      list = list.filter(
        (item) => item.sku.toLowerCase().includes(q) || item.name.toLowerCase().includes(q),
      )
    }

    if (statusFilter !== 'all') {
      list = list.filter((item) => getStatus(item.current_stock, item.reorder_threshold) === statusFilter)
    }

    return list.sort((a, b) => {
      const sa = STATUS_ORDER[getStatus(a.current_stock, a.reorder_threshold)]
      const sb = STATUS_ORDER[getStatus(b.current_stock, b.reorder_threshold)]
      if (sa !== sb) return sa - sb
      return a.sku.localeCompare(b.sku)
    })
  }, [inventory, search, statusFilter])

  const attentionCount = useMemo(() => {
    if (!inventory) return 0
    return inventory.filter((item) => getStatus(item.current_stock, item.reorder_threshold) !== 'healthy').length
  }, [inventory])

  if (error) {
    return (
      <div className="p-6 max-w-[1440px] w-full">
        <PageHeader title="Inventory" subtitle="Current stock levels and reorder thresholds." />
        <ErrorState
          title="Failed to load inventory"
          description={error instanceof Error ? error.message : 'Please check your connection and retry.'}
          onRetry={() => {
            void refetch()
          }}
        />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-[1440px] w-full">
      <PageHeader
        title="Inventory"
        subtitle="Current stock levels and reorder thresholds."
      />

      {/* Filter and search bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <div className="flex items-center gap-3 flex-wrap">
          {/* Status filter tabs */}
          <div className="flex items-center bg-white border border-border rounded-lg overflow-hidden shadow-xs">
            {STATUS_FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setStatusFilter(f.value)}
                className={`px-3.5 py-1.5 text-xs sm:text-sm font-medium transition-colors focus-visible:outline-none border-r border-border last:border-r-0 ${
                  statusFilter === f.value
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Search box */}
          <div className="relative">
            <Search className="w-4 h-4 text-text-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search SKU or name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-sm bg-white border border-border rounded-lg w-56 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 shadow-xs"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          {attentionCount > 0 && (
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-warning-50 text-warning-700 border border-warning-200">
              {attentionCount} SKU{attentionCount !== 1 ? 's' : ''} need attention
            </span>
          )}
          <span className="text-xs text-text-secondary">
            {items.length} item{items.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Inventory table */}
      <div className="bg-white border border-border rounded-[10px] overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px]">
            <thead>
              <tr className="border-b border-border bg-gray-50">
                <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  SKU
                </th>
                <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Product
                </th>
                <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Cost Price
                </th>
                <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Current Stock
                </th>
                <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Threshold
                </th>
                <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => <TableRowSkeleton key={i} cols={6} />)
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={6}>
                    <EmptyState
                      icon={Package}
                      title="No inventory records found."
                      description={search || statusFilter !== 'all' ? 'Try adjusting your filters.' : undefined}
                    />
                  </td>
                </tr>
              ) : (
                items.map((item) => {
                  const status = getStatus(item.current_stock, item.reorder_threshold)
                  return (
                    <tr key={item.sku} className="table-row-hover hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3.5">
                        <span className="font-mono-data text-sm text-gray-800 font-medium">
                          {item.sku}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="text-sm text-gray-700">{item.name}</span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span className="text-sm font-medium tabular-nums text-gray-600 font-mono-data">
                          {formatVND(item.cost_price)}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span
                          className={`text-sm font-bold tabular-nums ${
                            status === 'out'
                              ? 'text-critical-600'
                              : status === 'low'
                              ? 'text-warning-600'
                              : 'text-gray-800'
                          }`}
                        >
                          {item.current_stock}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span className="text-sm tabular-nums text-text-secondary">
                          {item.reorder_threshold}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <InventoryStatusBadge status={status} />
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
