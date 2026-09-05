import { useState } from 'react'
import {
  CircleDollarSign,
  Receipt,
  TrendingUp,
  ShoppingCart,
  ChevronRight,
  RefreshCw,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { PageHeader } from '../components/PageHeader'
import { MetricCard } from '../components/MetricCard'
import { Panel } from '../components/Panel'
import { ChannelBadge, SeverityBadge, InventoryStatusBadge } from '../components/Badge'
import { MetricCardSkeleton, ChartSkeleton, Skeleton } from '../components/Skeleton'
import { ErrorState } from '../components/ErrorState'
import { ChannelProfitChart } from '../features/dashboard/ChannelProfitChart'
import { ChannelRevenueChart } from '../features/dashboard/ChannelRevenueChart'
import { useDailyReport } from '../features/dashboard/api'
import { useInventory } from '../features/inventory/api'
import { useAlerts } from '../features/alerts/api'
import { useReconciliations } from '../features/reconciliation/api'
import { formatVND, formatDateTime } from '../utils'

function getInventoryStatus(current: number, threshold: number): 'out' | 'low' | 'healthy' {

  if (current === 0) return 'out'
  if (current <= threshold) return 'low'
  return 'healthy'
}

export function DashboardPage() {
  const navigate = useNavigate()
  const [selectedDate, setSelectedDate] = useState<string>('')

  const reportQuery = useDailyReport(selectedDate || undefined)
  const inventoryQuery = useInventory()
  const alertsQuery = useAlerts(false)
  const reconciliationsQuery = useReconciliations()

  const loading = reportQuery.isLoading || inventoryQuery.isLoading
  const error = reportQuery.error ?? inventoryQuery.error

  const handleRefresh = async () => {
    await Promise.all([
      reportQuery.refetch(),
      inventoryQuery.refetch(),
      alertsQuery.refetch(),
      reconciliationsQuery.refetch(),
    ])
  }

  if (error) {
    return (
      <div className="p-6 max-w-[1440px] w-full">
        <ErrorState
          title="Failed to load dashboard data"
          message={error.message}
          onRetry={() => {
            void handleRefresh()
          }}
        />
      </div>
    )
  }

  const report = reportQuery.data
  const activeAlerts = alertsQuery.data ?? []
  const reconciliations = reconciliationsQuery.data ?? []
  const inventory = inventoryQuery.data ?? []

  const atRiskInventory = inventory.filter(
    (i) => getInventoryStatus(i.current_stock, i.reorder_threshold) !== 'healthy'
  )

  const revenue = report?.totals.revenue ?? 0
  const cogs = report?.totals.cogs ?? 0
  const grossProfit = report?.totals.gross_profit ?? 0
  const orders = report?.totals.orders ?? 0
  const margin = revenue > 0 ? ((grossProfit / revenue) * 100).toFixed(1) : '0.0'

  return (
    <div className="p-6 max-w-[1440px] w-full">
      <PageHeader
        title="Dashboard"
        subtitle="Multichannel commerce performance and operational health."
        action={
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-border rounded-lg text-sm text-gray-700">
              <span className="text-text-secondary text-xs">Date:</span>
              <input
                type="date"
                value={selectedDate || report?.date || ''}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="font-medium bg-transparent border-0 p-0 text-sm text-gray-800 focus:outline-none cursor-pointer"
              />
            </div>
            <button
              onClick={() => {
                void handleRefresh()
              }}
              className="w-8 h-8 flex items-center justify-center rounded-lg border border-border bg-white text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-600"
              aria-label="Refresh data"
              title="Refresh data"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${reportQuery.isFetching ? 'animate-spin' : ''}`} />
            </button>
          </div>
        }
      />


      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <MetricCardSkeleton key={i} />)
        ) : (
          <>
            <MetricCard
              icon={CircleDollarSign}
              label="Revenue"
              value={formatVND(revenue, true)}
              subValue={formatVND(revenue)}
            />
            <MetricCard
              icon={Receipt}
              label="COGS"
              value={formatVND(cogs, true)}
              subValue={formatVND(cogs)}
            />
            <MetricCard
              icon={TrendingUp}
              label="Gross Profit"
              value={formatVND(grossProfit, true)}
              subValue={`${margin}% margin`}
            />
            <MetricCard
              icon={ShoppingCart}
              label="Orders"
              value={orders.toString()}
              subValue="across all channels"
            />
          </>
        )}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Panel
          title="Revenue by Channel"
          subtitle="Fixed channel colors keep comparisons familiar across visits."
        >
          {loading ? (
            <ChartSkeleton />
          ) : report && report.channels.length > 0 ? (
            <ChannelRevenueChart channels={report.channels} />
          ) : (
            <div className="py-12 text-center text-sm text-text-secondary">
              No revenue data available for this date.
            </div>
          )}
        </Panel>

        <Panel
          title="Gross Profit by Channel"
          subtitle="Positive and negative values diverge around zero."
        >
          {loading ? (
            <ChartSkeleton />
          ) : report && report.channels.length > 0 ? (
            <ChannelProfitChart channels={report.channels} />
          ) : (
            <div className="py-12 text-center text-sm text-text-secondary">
              No profit data available for this date.
            </div>
          )}
        </Panel>
      </div>

      {/* Channel Breakdown Table */}
      {report && report.channels.length > 0 && (
        <Panel title="Channel Performance Summary" className="mb-6" noPadding>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-gray-50">
                  <th className="px-4 py-3 text-left text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Channel
                  </th>
                  <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Orders
                  </th>
                  <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Revenue
                  </th>
                  <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    COGS
                  </th>
                  <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Gross Profit
                  </th>
                  <th className="px-4 py-3 text-right text-[12px] font-semibold text-text-secondary uppercase tracking-wide">
                    Margin
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {report.channels.map((ch) => {
                  const chMargin = ch.revenue > 0 ? ((ch.gross_profit / ch.revenue) * 100).toFixed(1) : '0.0'
                  return (
                    <tr key={ch.channel} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <ChannelBadge channel={ch.channel} />
                          <span className="text-sm font-medium text-gray-800">{ch.channel_name}</span>
                        </div>

                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span className="text-sm tabular-nums text-gray-700">{ch.orders}</span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span className="text-sm font-medium tabular-nums text-gray-800">{formatVND(ch.revenue)}</span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span className="text-sm tabular-nums text-gray-700">{formatVND(ch.cogs)}</span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span className={`text-sm font-semibold tabular-nums ${ch.gross_profit >= 0 ? 'text-success-700' : 'text-critical-600'}`}>
                          {formatVND(ch.gross_profit)}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span className="text-xs font-medium text-text-secondary tabular-nums">{chMargin}%</span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </Panel>
      )}

      {/* Operational Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {/* Inventory Health */}
        <Panel
          title="Inventory Health"
          subtitle="Products approaching or below reorder threshold."
          action={
            <button
              onClick={() => {
                void navigate('/inventory')
              }}
              className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium focus-visible:outline-none cursor-pointer"
            >
              View inventory <ChevronRight className="w-3.5 h-3.5" />
            </button>
          }

          noPadding
        >
          {inventoryQuery.isLoading ? (
            <div className="px-5 pb-5 space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-10 rounded-lg" />
              ))}
            </div>
          ) : atRiskInventory.length === 0 ? (
            <div className="px-5 py-8 text-center">
              <p className="text-sm text-success-600 font-medium">All stock levels healthy.</p>
            </div>
          ) : (
            <div className="divide-y divide-border">
              {atRiskInventory.map((item) => {
                const status = getInventoryStatus(item.current_stock, item.reorder_threshold)
                return (
                  <div key={item.sku} className="flex items-center justify-between px-5 py-3 gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono-data text-xs text-gray-800 font-medium">{item.sku}</span>
                        <InventoryStatusBadge status={status} />
                      </div>
                      <p className="text-xs text-text-secondary mt-0.5 truncate">{item.name}</p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <div
                        className={`text-sm font-bold tabular-nums ${
                          status === 'out' ? 'text-critical-600' : 'text-warning-600'
                        }`}
                      >
                        {item.current_stock} units
                      </div>
                      <div className="text-[11px] text-text-muted">threshold: {item.reorder_threshold}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </Panel>

        {/* Reconciliation Status */}
        <Panel
          title="Reconciliation Status"
          subtitle="Latest reconciliation run per source."
          action={
            <button
              onClick={() => {
                void navigate('/reconciliation')
              }}
              className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium focus-visible:outline-none cursor-pointer"
            >
              View reconciliation <ChevronRight className="w-3.5 h-3.5" />
            </button>
          }
          noPadding
        >
          {reconciliationsQuery.isLoading ? (
            <div className="px-5 pb-5 space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-14 rounded-lg" />
              ))}
            </div>
          ) : reconciliations.length === 0 ? (
            <div className="px-5 py-8 text-center text-sm text-text-secondary">
              No reconciliation runs recorded yet.
            </div>
          ) : (
            <div className="divide-y divide-border">
              {reconciliations.slice(0, 3).map((r) => (
                <div key={r.id} className="flex items-center justify-between px-5 py-3 gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-sm font-medium text-gray-800 capitalize">{r.source_system}</span>
                      <span
                        className={`inline-flex items-center gap-0.5 text-[11px] font-semibold px-1.5 py-0.5 rounded-md ${
                          r.status === 'success'
                            ? 'bg-success-50 text-success-700'
                            : r.status === 'mismatch'
                            ? 'bg-critical-50 text-critical-600'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {r.status === 'success' ? 'Success' : r.status === 'mismatch' ? 'Mismatch' : 'Failed'}
                      </span>
                    </div>
                    <p className="text-xs text-text-secondary">
                      {r.records_checked.toLocaleString()} records checked
                      {r.mismatches_found > 0 && (
                        <span className="text-critical-600 font-medium ml-1">
                          • {r.mismatches_found} mismatches
                        </span>
                      )}
                    </p>
                  </div>
                  {r.completed_at && (
                    <div className="text-[11px] text-text-muted text-right flex-shrink-0">
                      {formatDateTime(r.completed_at)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </Panel>
      </div>

      {/* Active Alerts */}
      <Panel
        title="Active Alerts"
        subtitle="Operational issues requiring attention."
        action={
          <button
            onClick={() => {
              void navigate('/alerts')
            }}
            className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium focus-visible:outline-none cursor-pointer"
          >
            View all alerts <ChevronRight className="w-3.5 h-3.5" />
          </button>
        }

        noPadding
      >
        {alertsQuery.isLoading ? (
          <div className="px-5 pb-5 space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-14 rounded-lg" />
            ))}
          </div>
        ) : activeAlerts.length === 0 ? (
          <div className="px-5 py-8 text-center">
            <p className="text-sm text-success-600 font-medium">No active alerts. Everything looks good.</p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {activeAlerts.map((alert) => (
              <div key={alert.id} className="flex items-start gap-3 px-5 py-3.5">
                <div className="flex-shrink-0 mt-0.5">
                  <SeverityBadge severity={alert.severity} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-semibold text-gray-700 mb-0.5 capitalize">
                    {alert.type.replace(/_/g, ' ')}
                  </div>
                  <p className="text-sm text-gray-600 leading-snug">{alert.message}</p>
                </div>
                <div className="text-[11px] text-text-muted flex-shrink-0 mt-0.5">
                  {formatDateTime(alert.created_at)}
                </div>
              </div>
            ))}
          </div>
        )}
      </Panel>
    </div>
  )
}
