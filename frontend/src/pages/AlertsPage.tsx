import { useMemo, useState } from 'react'
import { Bell, CheckCircle2, TriangleAlert } from 'lucide-react'

import { SeverityBadge } from '../components/Badge'
import { Button } from '../components/Button'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { PageHeader } from '../components/PageHeader'
import { TableRowSkeleton } from '../components/Skeleton'
import { useToast } from '../components/Toast'
import { useAlerts, useResolveAlert } from '../features/alerts/api'
import type { AlertStatus } from '../types'
import { formatDateTime } from '../utils'

const STATUS_FILTERS: Array<{ value: AlertStatus | 'all'; label: string }> = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'resolved', label: 'Resolved' },
]

export function AlertsPage() {
  const [statusFilter, setStatusFilter] = useState<AlertStatus | 'all'>('active')
  const [confirmId, setConfirmId] = useState<number | null>(null)
  const { addToast } = useToast()

  const resolvedParam = useMemo(() => {
    if (statusFilter === 'active') return false
    if (statusFilter === 'resolved') return true
    return undefined
  }, [statusFilter])

  const { data: alerts, isLoading, error, refetch } = useAlerts(resolvedParam)
  const resolveMutation = useResolveAlert()

  const handleResolve = async (id: number) => {
    try {
      await resolveMutation.mutateAsync(id)
      setConfirmId(null)
      addToast({
        type: 'success',
        message: 'Alert resolved successfully.',
      })
    } catch (err) {
      addToast({
        type: 'error',
        message: err instanceof Error ? err.message : 'Failed to resolve alert.',
      })
    }
  }

  if (error) {
    return (
      <div className="p-6 max-w-[1440px] w-full">
        <PageHeader title="Alerts" subtitle="Operational issues requiring attention." />
        <ErrorState
          title="Failed to load alerts"
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
        title="Alerts"
        subtitle="Operational issues requiring attention."
      />

      {/* Filter bar */}
      <div className="flex items-center gap-3 mb-5">
        <div className="flex items-center bg-white border border-border rounded-lg overflow-hidden shadow-xs">
          {STATUS_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setStatusFilter(f.value)}
              className={`px-4 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none border-r border-border last:border-r-0 ${
                statusFilter === f.value
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
        <span className="text-xs text-text-secondary ml-auto">
          {alerts?.length ?? 0} alert{(alerts?.length ?? 0) !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Alert list */}
      <div className="bg-white border border-border rounded-[10px] overflow-hidden shadow-xs">
        {isLoading ? (
          <table className="w-full">
            <tbody className="divide-y divide-border">
              {Array.from({ length: 5 }).map((_, i) => (
                <TableRowSkeleton key={i} cols={4} />
              ))}
            </tbody>
          </table>
        ) : !alerts || alerts.length === 0 ? (
          <EmptyState
            icon={TriangleAlert}
            title={statusFilter === 'active' ? 'No active alerts.' : 'No alerts found.'}
            description={statusFilter === 'active' ? 'Everything looks healthy and operational.' : undefined}
          />
        ) : (
          <div className="divide-y divide-border">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="flex flex-col sm:flex-row items-start gap-4 px-5 py-4 hover:bg-gray-50 transition-colors"
              >
                {/* Severity */}
                <div className="flex-shrink-0 pt-0.5 w-[72px]">
                  <SeverityBadge severity={alert.severity} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="text-sm font-semibold text-gray-800 uppercase tracking-wide">
                      {alert.type.replace(/_/g, ' ')}
                    </span>
                    <span
                      className={`text-[11px] font-medium flex items-center gap-1 ${
                        alert.resolved ? 'text-success-600' : 'text-text-muted'
                      }`}
                    >
                      • {alert.resolved ? 'Resolved' : 'Active'}
                    </span>
                    {alert.notified_at && (
                      <span className="text-[11px] text-gray-400 flex items-center gap-1">
                        <Bell className="w-3 h-3 text-gray-400" />
                        Notified
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700 leading-snug">{alert.message}</p>
                  <p className="text-[11px] text-text-muted mt-1.5 font-mono-data">
                    {formatDateTime(alert.created_at)}
                    {alert.resolved_at && ` • Resolved at ${formatDateTime(alert.resolved_at)}`}
                  </p>
                </div>

                {/* Action */}
                <div className="flex-shrink-0 pt-0.5 self-end sm:self-auto">
                  {!alert.resolved ? (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setConfirmId(alert.id)}
                      disabled={resolveMutation.isPending}
                    >
                      Resolve
                    </Button>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs text-success-600 font-medium bg-success-50 px-2.5 py-1 rounded-md border border-success-200">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Resolved
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Confirm Dialog */}
      {confirmId !== null && (
        <ConfirmDialog
          title="Resolve this alert?"
          description="This marks the alert as resolved in MCO. The alert will not re-trigger unless a new threshold violation occurs."
          confirmLabel="Resolve alert"
          cancelLabel="Cancel"
          loading={resolveMutation.isPending}
          onConfirm={() => {
            void handleResolve(confirmId)
          }}
          onCancel={() => setConfirmId(null)}
        />
      )}
    </div>
  )
}
