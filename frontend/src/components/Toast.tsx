import { useEffect } from "react"
import { CheckCircle, XCircle, Info, X } from "lucide-react"
import type { ToastItem } from "@/types"

export interface ToastProps {
  toast: ToastItem
  onDismiss: (id: number) => void
}

export function Toast({ toast, onDismiss }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), 4000)
    return () => clearTimeout(timer)
  }, [toast.id, onDismiss])

  const iconMap = {
    success: <CheckCircle className="w-4 h-4 text-success-600 flex-shrink-0" />,
    error: <XCircle className="w-4 h-4 text-critical-600 flex-shrink-0" />,
    info: <Info className="w-4 h-4 text-info-600 flex-shrink-0" />,
  }

  return (
    <div className="flex items-start gap-2.5 bg-white border border-border rounded-lg px-3.5 py-3 shadow-md min-w-[260px] max-w-[360px]">
      {iconMap[toast.type]}
      <span className="text-sm text-gray-800 flex-1 leading-snug">{toast.message}</span>
      <button
        onClick={() => onDismiss(toast.id)}
        className="text-gray-400 hover:text-gray-600 flex-shrink-0 focus-visible:outline-none"
        aria-label="Dismiss"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}

export interface ToastContainerProps {
  toasts: ToastItem[]
  onDismiss: (id: number) => void
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) return null
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <Toast key={t.id} toast={t} onDismiss={onDismiss} />
      ))}
    </div>
  )
}
