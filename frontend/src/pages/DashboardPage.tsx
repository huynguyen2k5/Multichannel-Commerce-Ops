import { useState } from 'react'

import { AsyncState } from '../components/AsyncState'
import { PageHeader } from '../components/PageHeader'
import { Panel } from '../components/Panel'
import { useAlerts } from '../features/alerts/api'
import { ChannelProfitChart } from '../features/dashboard/ChannelProfitChart'
import { ChannelRevenueChart } from '../features/dashboard/ChannelRevenueChart'
import { MetricCard } from '../features/dashboard/MetricCard'
import { useDailyReport } from '../features/dashboard/api'
import { useInventory } from '../features/inventory/api'
import { useReconciliations } from '../features/reconciliation/api'
import { formatCurrency, formatInteger, formatTimestamp } from '../lib/format'

const DEFAULT_DATE =
  (import.meta.env.VITE_DEMO_REPORT_DATE as string | undefined) ?? '2026-09-01'

export function DashboardPage() {
  const [date, setDate] = useState(DEFAULT_DATE)
  const report = useDailyReport(date)
  const inventory = useInventory()
  const alerts = useAlerts(false)
  const reconciliations = useReconciliations()

  const isLoading = report.isLoading || inventory.isLoading || alerts.isLoading || reconciliations.isLoading
  const error = report.error ?? inventory.error ?? alerts.error ?? reconciliations.error

  const lowStock = (inventory.data ?? []).filter((item) => item.is_low_stock)
  const latestReconciliation = reconciliations.data?.[0]

  return (
    <>
      <PageHeader
        eyebrow="Daily operations"
        title="Operations dashboard"
        description="Revenue, margin, inventory health and data-integrity signals in one action-oriented view."
        action={
          <label className="flex items-center gap-2 text-xs text-slate-400">
            Report date
            <input
              type="date"
              value={date}
              onChange={(event) => setDate(event.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-500 focus:ring-2"
            />
          </label>
        }
      />

      <AsyncState isLoading={isLoading} error={error}>
        {report.data ? (
          <div className="space-y-6">
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <MetricCard label="Revenue" value={formatCurrency(report.data.totals.revenue)} />
              <MetricCard label="COGS" value={formatCurrency(report.data.totals.cogs)} />
              <MetricCard label="Gross profit" value={formatCurrency(report.data.totals.gross_profit)} />
              <MetricCard label="Orders" value={formatInteger(report.data.totals.orders)} />
            </section>

            <section className="grid gap-6 xl:grid-cols-2">
              <Panel title="Revenue by channel" subtitle="Fixed channel colors keep comparisons familiar across visits.">
                <ChannelRevenueChart channels={report.data.channels} />
              </Panel>
              <Panel title="Gross profit by channel" subtitle="Positive and negative values diverge around zero.">
                <ChannelProfitChart channels={report.data.channels} />
              </Panel>
            </section>

            <section className="grid gap-6 xl:grid-cols-2">
              <Panel title="Inventory health" subtitle={`${lowStock.length} SKU(s) at or below reorder threshold`}>
                {lowStock.length ? (
                  <ul className="divide-y divide-slate-800">
                    {lowStock.slice(0, 6).map((item) => (
                      <li key={item.product_id} className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0">
                        <div>
                          <p className="text-sm font-medium text-slate-200">{item.sku}</p>
                          <p className="text-xs text-slate-500">{item.name}</p>
                        </div>
                        <span className="rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-medium text-amber-300">
                          {item.current_stock} left
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-emerald-300">All seeded products are above their reorder thresholds.</p>
                )}
              </Panel>

              <Panel title="Data integrity" subtitle="Latest automated reconciliation run">
                {latestReconciliation ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-medium text-slate-200">{latestReconciliation.source_system}</p>
                        <p className="text-xs text-slate-500">{formatTimestamp(latestReconciliation.completed_at)}</p>
                      </div>
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                          latestReconciliation.status === 'success'
                            ? 'bg-emerald-500/10 text-emerald-300'
                            : 'bg-red-500/10 text-red-300'
                        }`}
                      >
                        {latestReconciliation.status}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400">
                      Checked {latestReconciliation.records_checked} source records and found{' '}
                      <strong className="text-slate-200">{latestReconciliation.mismatches_found}</strong> mismatch(es).
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">No reconciliation run has been recorded yet.</p>
                )}
              </Panel>
            </section>

            <Panel title="Active alerts" subtitle="Operational exceptions that still need attention">
              {alerts.data?.length ? (
                <div className="grid gap-3 lg:grid-cols-2">
                  {alerts.data.slice(0, 6).map((alert) => (
                    <div key={alert.id} className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{alert.type.replaceAll('_', ' ')}</span>
                        <span className={alert.severity === 'critical' ? 'text-xs text-red-300' : 'text-xs text-amber-300'}>{alert.severity}</span>
                      </div>
                      <p className="mt-2 text-sm leading-6 text-slate-300">{alert.message}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-emerald-300">No active alerts.</p>
              )}
            </Panel>
          </div>
        ) : null}
      </AsyncState>
    </>
  )
}
