import { AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/Button"

export interface ErrorStateProps {
  title?: string
  description?: string
  message?: string
  onRetry?: () => void
  requestId?: string
}

export function ErrorState({
  title = "Unable to load data.",
  description,
  message,
  onRetry,
  requestId,
}: ErrorStateProps) {
  const desc = description ?? message ?? "Check the API connection and try again."
  return (
    <div className="flex flex-col items-center justify-center py-14 px-6 text-center">
      <div className="w-10 h-10 rounded-xl bg-critical-50 flex items-center justify-center mb-3">
        <AlertCircle className="w-5 h-5 text-critical-600" />
      </div>
      <p className="text-sm font-medium text-gray-800 mb-1">{title}</p>
      <p className="text-xs text-text-secondary max-w-xs mb-4">{desc}</p>

      {onRetry && (
        <Button
          variant="secondary"
          size="sm"
          icon={<RefreshCw className="w-3.5 h-3.5" />}
          onClick={onRetry}
        >
          Retry
        </Button>
      )}
      {requestId && (
        <p className="mt-3 text-[11px] text-text-muted font-mono-data">Request ID: {requestId}</p>
      )}
    </div>
  )
}
