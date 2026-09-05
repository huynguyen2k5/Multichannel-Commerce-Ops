import { ArrowLeft, CheckCircle2, XCircle } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'

import { ReconciliationStatusBadge } from '../components/Badge'
import { ErrorState } from '../components/ErrorState'
import { ApiError } from '../lib/api'
import { Panel } from '../components/Panel'
import { Skeleton } from '../components/Skeleton'
import { useReconciliation } from '../features/reconciliation/api'
import { formatDateTime, formatVND } from '../utils'

interface MismatchLabels {
  expectedLabel: string
  actualLabel: string
  basis: string | null
}

function getMismatchLabels(code: string): MismatchLabels {
  switch (code) {
    case 'REVENUE_MISMATCH':
      return { expectedLabel: 'Expected Revenue', actualLabel: 'Actual Revenue', basis: 'Source Order' }
    case 'COGS_MISMATCH':
      return { expectedLabel: 'Expected COGS', actualLabel: 'Actual COGS', basis: 'Order Item Cost Snapshot' }
    case 'TOTAL_MISMATCH':
      return { expectedLabel: 'Expected Total', actualLabel: 'Actual Total', basis: 'Channel Checkout' }
    case 'MISSING_ORDER':
      return { expectedLabel: 'Source Order', actualLabel: 'MCO Record', basis: 'External Order ID' }
    default:
      return { expectedLabel: 'Expected', actualLabel: 'Actual', basis: null }
  }
}

export function ReconciliationDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const numericId = id ? parseInt(id, 10) : undefined
  const { data: run, isLoading, error, refetch } = useReconciliation(numericId)

  if (isLoading) {
    return (
      <div className="p-6 max-w-[960px] w-full space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Skeleton className="h-4 w-32" />
        </div>
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-40 w-full rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    )
  }

  if (error || !run) {
    return (
      <div className="p-6 max-w-[960px] w-full">
        <button
          onClick={() => {
            void navigate('/reconciliation')
          }}
          className="flex items-center gap-1.5 text-sm text-text-secondary hover:text-gray-700 transition-colors mb-4 focus-visible:outline-none"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Reconciliation
        </button>
        <ErrorState
          title="Reconciliation run not found"
          description={error instanceof Error ? error.message : `Run #${id ?? ''} could not be loaded.`}
          requestId={error instanceof ApiError ? error.requestId : undefined}
          onRetry={() => {
            void refetch()
          }}
        />
      </div>
    )
  }

  const mismatches = run.detail_json.mismatches ?? []

  return (
    <div className="p-6 max-w-[960px] w-full">
      <button
        onClick={() => {
          void navigate('/reconciliation')
        }}
        className="flex items-center gap-1.5 text-sm text-text-secondary hover:text-gray-700 transition-colors mb-4 focus-visible:outline-none"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        Back to Reconciliation
      </button>

      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reconciliation Run #{run.id}</h1>
          <p className="text-sm text-text-secondary mt-1">Source: {run.source_system}</p>
        </div>
        <ReconciliationStatusBadge status={run.status} />
      </div>

      {/* Summary Panel */}
      <Panel className="mb-6 shadow-xs">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-text-secondary mb-1">Source System</p>
            <p className="text-sm font-semibold text-gray-800">{run.source_system}</p>
          </div>
          <div>
            <p className="text-xs text-text-secondary mb-1">Started</p>
            <p className="text-sm text-gray-700 font-mono-data">{formatDateTime(run.started_at)}</p>
          </div>
          <div>
            <p className="text-xs text-text-secondary mb-1">Completed</p>
            <p className="text-sm text-gray-700 font-mono-data">
              {run.completed_at ? formatDateTime(run.completed_at) : <span className="text-text-muted">In progress</span>}
            </p>
          </div>
          <div>
            <p className="text-xs text-text-secondary mb-1">Records Checked</p>
            <p className="text-sm font-semibold tabular-nums text-gray-800 font-mono-data">
              {run.records_checked.toLocaleString()}
            </p>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs text-text-secondary">Mismatches detected:</span>
            <span
              className={`text-sm font-bold tabular-nums font-mono-data ${
                run.mismatches_found > 0 ? 'text-critical-600' : 'text-success-700'
              }`}
            >
              {run.mismatches_found}
            </span>
          </div>
          <span className="text-xs text-text-muted">
            Run ID: #{run.id}
          </span>
        </div>
      </Panel>

      {/* Clean Match View */}
      {run.status === 'success' && (
        <Panel className="shadow-xs">
          <div className="flex flex-col items-center py-8 text-center">
            <div className="w-12 h-12 rounded-full bg-success-50 flex items-center justify-center mb-3">
              <CheckCircle2 className="w-6 h-6 text-success-600" />
            </div>
            <p className="text-base font-semibold text-success-700">Reconciliation Successful</p>
            <p className="text-sm text-text-secondary mt-1 max-w-md">
              All {run.records_checked} record(s) matched between {run.source_system} and MCO ledgers. No discrepancies found.
            </p>
          </div>
        </Panel>
      )}

      {/* Mismatches Detail View */}
      {mismatches.length > 0 && (
        <Panel
          title="Mismatch Details"
          subtitle="Records where source values deviate from internal ledger calculations."
          noPadding
          className="shadow-xs"
        >
          <div className="divide-y divide-border">
            {mismatches.map((mismatch, i) => {
              const labels = getMismatchLabels(mismatch.code)
              const expVal = mismatch.expected != null ? parseFloat(mismatch.expected) : null
              const actVal = mismatch.actual != null ? parseFloat(mismatch.actual) : null
              const diff = expVal !== null && actVal !== null && !isNaN(expVal) && !isNaN(actVal) ? actVal - expVal : null

              return (
                <div key={i} className="px-5 py-4">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono-data text-sm font-bold text-gray-800">
                        {mismatch.external_order_id}
                      </span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-critical-50 text-critical-600 border border-critical-200 uppercase tracking-wide">
                        {mismatch.code.replace(/_/g, ' ')}
                      </span>
                    </div>
                    {diff !== null && (
                      <span
                        className={`text-sm font-bold tabular-nums font-mono-data flex-shrink-0 ${
                          diff < 0 ? 'text-critical-600' : 'text-warning-600'
                        }`}
                      >
                        {diff > 0 ? '+' : ''}
                        {formatVND(diff)}
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="bg-gray-50 rounded-lg px-3.5 py-2.5 border border-gray-100">
                      <p className="text-[11px] text-text-muted mb-0.5">{labels.expectedLabel}</p>
                      {labels.basis && (
                        <p className="text-[10px] text-text-muted mb-1 leading-tight">Basis: {labels.basis}</p>
                      )}
                      <p className="text-sm font-medium tabular-nums text-gray-800 font-mono-data">
                        {expVal !== null && !isNaN(expVal) ? formatVND(expVal) : mismatch.expected ?? '—'}
                      </p>
                    </div>

                    <div className="bg-gray-50 rounded-lg px-3.5 py-2.5 border border-gray-100">
                      <p className="text-[11px] text-text-muted mb-1">{labels.actualLabel}</p>
                      <p className="text-sm font-medium tabular-nums text-gray-800 font-mono-data">
                        {actVal !== null && !isNaN(actVal) ? formatVND(actVal) : mismatch.actual ?? '—'}
                      </p>
                    </div>

                    <div
                      className={`rounded-lg px-3.5 py-2.5 border ${
                        diff !== null && diff < 0
                          ? 'bg-critical-50 border-critical-100'
                          : 'bg-warning-50 border-warning-100'
                      }`}
                    >
                      <p className="text-[11px] text-text-muted mb-1">Difference</p>
                      <p
                        className={`text-sm font-bold tabular-nums font-mono-data ${
                          diff !== null && diff < 0 ? 'text-critical-600' : 'text-warning-600'
                        }`}
                      >
                        {diff !== null
                          ? `${diff > 0 ? '+' : ''}${formatVND(diff)}`
                          : mismatch.actual === null
                          ? 'Missing Record'
                          : 'Value Mismatch'}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </Panel>
      )}

      {/* Run Failure State */}
      {run.status === 'failed' && (
        <Panel className="shadow-xs">
          <div className="flex flex-col items-center py-8 text-center">
            <div className="w-12 h-12 rounded-full bg-critical-50 flex items-center justify-center mb-3">
              <XCircle className="w-6 h-6 text-critical-600" />
            </div>
            <p className="text-base font-semibold text-critical-600">Reconciliation Failed</p>
            <p className="text-sm text-text-secondary mt-1 max-w-md">
              The reconciliation run encountered an error and could not complete. Check source system connectivity and retry.
            </p>
          </div>
        </Panel>
      )}
    </div>
  )
}
