import type { LucideIcon } from "lucide-react"

export interface MetricCardProps {
  icon?: LucideIcon
  label: string
  value: string | number
  subValue?: string
  hint?: string
  valueClassName?: string
  iconClassName?: string
  className?: string
}

export function MetricCard({
  icon: Icon,
  label,
  value,
  subValue,
  hint,
  valueClassName = "text-gray-900",
  iconClassName = "bg-gray-100 text-gray-500",
  className = "",
}: MetricCardProps) {
  const subtitle = subValue || hint

  return (
    <div className={`bg-white border border-border rounded-[10px] p-5 shadow-xs ${className}`}>
      <div className="flex items-center gap-2.5 mb-3">
        {Icon && (
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${iconClassName}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
        <span className="text-xs font-medium text-text-secondary">{label}</span>
      </div>
      <div className={`text-2xl font-bold tabular-nums leading-none mb-1 ${valueClassName}`}>
        {value}
      </div>
      {subtitle && (
        <div className="text-xs text-text-muted mt-1">{subtitle}</div>
      )}
    </div>
  )
}
