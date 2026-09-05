import type React from "react"

export interface SkeletonProps {
  className?: string
  style?: React.CSSProperties
}

export function Skeleton({ className = "", style }: SkeletonProps) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${className}`} style={style} />
  )
}

export function MetricCardSkeleton() {
  return (
    <div className="bg-white border border-border rounded-[10px] p-5 shadow-xs">
      <div className="flex items-center gap-2 mb-3">
        <Skeleton className="w-8 h-8 rounded-lg" />
        <Skeleton className="w-20 h-3.5 rounded" />
      </div>
      <Skeleton className="w-32 h-8 rounded mb-1.5" />
      <Skeleton className="w-16 h-3 rounded" />
    </div>
  )
}

export function TableRowSkeleton({ cols = 6 }: { cols?: number }) {
  return (
    <tr>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-3.5 rounded" style={{ width: i === 0 ? "80px" : i === cols - 1 ? "60px" : "120px" }} />
        </td>
      ))}
    </tr>
  )
}

export function ChartSkeleton({ height = 220 }: { height?: number }) {
  return (
    <div className="flex items-end gap-3 px-2" style={{ height }}>
      {[60, 80, 50, 75, 45].map((h, i) => (
        <div key={i} className="flex-1 flex items-end">
          <Skeleton className="w-full rounded-sm" style={{ height: `${h}%` }} />
        </div>
      ))}
    </div>
  )
}
