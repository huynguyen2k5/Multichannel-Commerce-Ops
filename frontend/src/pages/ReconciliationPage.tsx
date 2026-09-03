import { AsyncState } from '../components/AsyncState'
import { PageHeader } from '../components/PageHeader'
import { Panel } from '../components/Panel'
import { useReconciliations } from '../features/reconciliation/api'
import { formatTimestamp } from '../lib/format'

export function ReconciliationPage() {
  const query = useReconciliations()

  return (
    <>
      <PageHeader
        eyebrow="Data integrity"
        title="Reconciliation"
        description="Source snapshots are compared with normalized orders, revenue entries and COGS snapshots. Mismatches remain inspectable after each run."
      />
      <AsyncState isLoading={query.isLoading} error={query.error}>
        <Panel title="Run history" subtitle={`${query.data?.length ?? 0} recorded reconciliation run(s)`}>
          {query.data?.length ? (
            <div className="space-y-3">
              {query.data.map((run) => {
                const mismatches = run.detail_json.mismatches ?? []
                const isHealthy = run.status === 'success'
                return (
                  <details key={run.id} className="group rounded-xl border border-slate-800 bg-slate-950/45 open:border-slate-700">
                    <summary className="flex cursor-pointer list-none flex-wrap items-center justify-between gap-4 px-4 py-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-slate-100">{run.source_system}</span>
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${isHealthy ? 'bg-emerald-500/10 text-emerald-300' : 'bg-red-500/10 text-red-300'}`}>
                            {run.status}
                          </span>
                        </div>
                        <p className="mt-1 text-xs text-slate-500">{formatTimestamp(run.completed_at)}</p>
                      </div>
                      <div className="text-right text-xs text-slate-400">
                        <p>{run.records_checked} records checked</p>
                        <p className={run.mismatches_found ? 'mt-1 text-red-300' : 'mt-1 text-emerald-300'}>
                          {run.mismatches_found} mismatch(es)
                        </p>
                      </div>
                    </summary>
                    <div className="border-t border-slate-800 px-4 py-4">
                      {mismatches.length ? (
                        <div className="overflow-x-auto">
                          <table className="w-full min-w-[620px] text-left text-sm">
                            <thead className="text-xs uppercase tracking-wider text-slate-500">
                              <tr>
                                <th className="pb-2 font-medium">Order</th>
                                <th className="pb-2 font-medium">Mismatch</th>
                                <th className="pb-2 font-medium">Expected</th>
                                <th className="pb-2 font-medium">Actual</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/80">
                              {mismatches.map((mismatch, index) => (
                                <tr key={`${mismatch.external_order_id}-${mismatch.code}-${index}`}>
                                  <td className="py-2.5 font-medium text-slate-200">{mismatch.external_order_id}</td>
                                  <td className="py-2.5 text-red-300">{mismatch.code}</td>
                                  <td className="py-2.5 text-slate-400">{mismatch.expected ?? '—'}</td>
                                  <td className="py-2.5 text-slate-400">{mismatch.actual ?? '—'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <p className="text-sm text-emerald-300">No mismatch detail recorded for this run.</p>
                      )}
                    </div>
                  </details>
                )
              })}
            </div>
          ) : (
            <p className="py-8 text-center text-sm text-slate-500">No reconciliation has run yet.</p>
          )}
        </Panel>
      </AsyncState>
    </>
  )
}
