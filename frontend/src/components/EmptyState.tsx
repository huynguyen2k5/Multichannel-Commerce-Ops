import type React from "react"
import type { LucideIcon } from "lucide-react"
import { Inbox } from "lucide-react"

export interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: React.ReactNode
}

export function EmptyState({ icon: Icon = Inbox, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center mb-3">
        <Icon className="w-5 h-5 text-gray-400" />
      </div>
      <p className="text-sm font-medium text-gray-700 mb-1">{title}</p>
      {description && (
        <p className="text-xs text-text-secondary max-w-xs">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
