import type React from "react"

export interface PanelProps {
  title?: string
  subtitle?: string
  action?: React.ReactNode
  children: React.ReactNode
  className?: string
  noPadding?: boolean
}

export function Panel({ title, subtitle, action, children, className = "", noPadding = false }: PanelProps) {
  return (
    <div className={`bg-white border border-border rounded-[10px] overflow-hidden ${className}`}>
      {(title || subtitle || action) && (
        <div className="flex items-start justify-between gap-4 px-5 py-4 border-b border-border">
          <div className="min-w-0">
            {title && <h3 className="text-sm font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="text-xs text-text-secondary mt-0.5">{subtitle}</p>}
          </div>
          {action && <div className="flex-shrink-0">{action}</div>}
        </div>
      )}
      <div className={noPadding ? "" : "p-5"}>{children}</div>
    </div>
  )
}
