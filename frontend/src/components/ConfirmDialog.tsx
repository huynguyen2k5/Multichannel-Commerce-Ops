import { X } from "lucide-react"
import { Button } from "@/components/Button"

export interface ConfirmDialogProps {
  title: string
  description?: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: "primary" | "danger"
  loading?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "primary",
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/30 backdrop-blur-[1px]"
        onClick={onCancel}
      />
      {/* Dialog */}
      <div className="relative bg-white rounded-xl border border-border shadow-xl w-[380px] mx-4">
        <div className="flex items-start justify-between px-5 pt-5 pb-4">
          <h3 className="text-sm font-semibold text-gray-900 pr-4">{title}</h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 focus-visible:outline-none"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        {description && (
          <p className="px-5 pb-4 text-sm text-text-secondary leading-relaxed border-b border-border">{description}</p>
        )}
        <div className="flex items-center justify-end gap-2 px-5 py-4">
          <Button variant="secondary" size="sm" onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </Button>
          <Button variant={variant} size="sm" loading={loading} onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  )
}
