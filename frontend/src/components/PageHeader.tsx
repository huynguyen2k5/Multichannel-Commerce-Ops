import type React from "react"

export interface PageHeaderProps {
  title: string
  subtitle?: string
  description?: string
  eyebrow?: string
  action?: React.ReactNode
  className?: string
}

export function PageHeader({ title, subtitle, description, eyebrow, action, className = "" }: PageHeaderProps) {
  const sub = subtitle || description

  return (
    <div className={`flex items-start justify-between gap-4 mb-6 ${className}`}>
      <div>
        {eyebrow && (
          <div className="text-[11px] uppercase tracking-wider font-semibold text-primary-600 mb-1">
            {eyebrow}
          </div>
        )}
        <h1 className="text-2xl font-bold text-gray-900 leading-tight">{title}</h1>
        {sub && <p className="text-sm text-text-secondary mt-1">{sub}</p>}
      </div>
      {action && <div className="flex items-center gap-2 flex-shrink-0">{action}</div>}
    </div>
  )
}
