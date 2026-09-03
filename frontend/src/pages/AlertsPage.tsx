import { AsyncState } from '../components/AsyncState'
import { PageHeader } from '../components/PageHeader'
import { Panel } from '../components/Panel'
import { useAlerts, useResolveAlert } from '../features/alerts/api'
import { formatTimestamp } from '../lib/format'

const severityClass = {
  info: 'border-cyan-500/25 bg-cyan-500/5 text-cyan-300',
  warning: 'border-amber-500/25 bg-amber-500/5 text-amber-300',
  critical: 'border-red-500/25 bg-red-500/5 text-red-300',
} as const

export function AlertsPage() {
  const query = useAlerts(false)
  const resolveAlert = useResolveAlert()

  return (
    <>
      <PageHeader
        eyebrow="Exception management"
        title="Active alerts"
        description="Alerts are deduplicated while active so scheduled workflows do not flood operators with the same condition."
      />
      <AsyncState isLoading={query.isLoading} error={query.error}>
        <Panel title="Needs attention" subtitle={`${query.data?.length ?? 0} unresolved alert(s)`}>
          {query.data?.length ? (
            <div className="grid gap-4 xl:grid-cols-2">
              {query.data.map((alert) => (
                <article key={alert.id} className={`rounded-xl border p-4 ${severityClass[alert.severity]}`}>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] opacity-80">
                        {alert.type.replaceAll('_', ' ')}
                      </p>
                      <p className="mt-2 text-sm leading-6 text-slate-200">{alert.message}</p>
                    </div>
                    <span className="rounded-full bg-slate-950/50 px-2 py-1 text-[11px] font-medium uppercase">
                      {alert.severity}
                    </span>
                  </div>
                  <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-current/10 pt-3">
                    <div className="text-xs opacity-70">
                      <span>{formatTimestamp(alert.created_at)}</span>
                      <span className="mx-2">·</span>
                      <span>{alert.notified_at ? 'Telegram notified' : 'Notification pending'}</span>
                    </div>
                    <button
                      type="button"
                      disabled={resolveAlert.isPending}
                      onClick={() => resolveAlert.mutate(alert.id)}
                      className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Resolve
                    </button>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-5 text-sm text-emerald-300">
              No active operational alerts.
            </div>
          )}
          {resolveAlert.error ? (
            <p className="mt-4 text-sm text-red-300">Failed to resolve alert. Retry after checking backend health.</p>
          ) : null}
        </Panel>
      </AsyncState>
    </>
  )
}
