import { LayoutDashboard, ShoppingBag, Package, TriangleAlert, ListChecks } from "lucide-react"
import { Link, useLocation } from "react-router-dom"
import type { Page } from "@/types"

interface NavItem {
  id: Page
  path: string
  label: string
  icon: typeof LayoutDashboard
}

const NAV_ITEMS: NavItem[] = [
  { id: "dashboard", path: "/", label: "Dashboard", icon: LayoutDashboard },
  { id: "orders", path: "/orders", label: "Orders", icon: ShoppingBag },
  { id: "inventory", path: "/inventory", label: "Inventory", icon: Package },
  { id: "alerts", path: "/alerts", label: "Alerts", icon: TriangleAlert },
  { id: "reconciliation", path: "/reconciliation", label: "Reconciliation", icon: ListChecks },
]

export interface SystemStatusInfo {
  label: string
  color: string
}

export interface SidebarProps {
  currentPage?: Page
  onNavigate?: (page: Page) => void
  activeAlerts?: { critical: number; warning: number; total: number }
}

export function Sidebar({ currentPage, onNavigate, activeAlerts }: SidebarProps) {
  const location = useLocation()
  const currentPath = location.pathname

  // Determine active item either by currentPage prop or by react-router pathname
  const activeId = (() => {
    if (currentPage) return currentPage
    if (currentPath.startsWith("/orders")) return "orders"
    if (currentPath.startsWith("/inventory")) return "inventory"
    if (currentPath.startsWith("/alerts")) return "alerts"
    if (currentPath.startsWith("/reconciliation")) return "reconciliation"
    return "dashboard"
  })()

  // Dynamic system status
  const status: SystemStatusInfo = (() => {
    if (activeAlerts) {
      if (activeAlerts.critical > 0) return { label: `${activeAlerts.critical} critical issues detected`, color: "bg-critical-600" }
      if (activeAlerts.warning > 0) return { label: `${activeAlerts.warning} alerts require attention`, color: "bg-warning-600" }
      return { label: "All systems operational", color: "bg-success-600" }
    }
    return { label: "All systems operational", color: "bg-success-600" }
  })()

  return (
    <aside className="w-[248px] flex-shrink-0 h-full bg-white border-r border-border flex flex-col shadow-xs select-none">
      {/* Logo */}
      <div className="px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-primary-600 rounded-lg flex items-center justify-center flex-shrink-0 shadow-xs">
            <span className="text-white text-xs font-bold leading-none">M</span>
          </div>
          <div>
            <div className="text-sm font-bold text-gray-900 leading-none">MCO</div>
            <div className="text-[10px] text-text-secondary leading-none mt-0.5">Commerce Operations</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-3 overflow-y-auto">
        <div className="space-y-0.5">
          {NAV_ITEMS.map(({ id, path, label, icon: Icon }) => {
            const isActive = activeId === id
            const content = (
              <>
                <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? "text-primary-600" : "text-gray-400"}`} />
                <span className="flex-1">{label}</span>
                {id === "alerts" && activeAlerts && activeAlerts.total > 0 && (
                  <span className={`text-[10px] font-semibold px-1.5 py-0.2 rounded-full ${activeAlerts.critical > 0 ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"}`}>
                    {activeAlerts.total}
                  </span>
                )}
              </>
            )

            const className = `w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-100 text-left
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-600 focus-visible:ring-offset-1
              ${isActive
                ? "bg-primary-50 text-primary-700 font-semibold"
                : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              }`

            if (onNavigate) {
              return (
                <button
                  key={id}
                  onClick={() => onNavigate(id)}
                  className={className}
                >
                  {content}
                </button>
              )
            }

            return (
              <Link
                key={id}
                to={path}
                className={className}
              >
                {content}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-border bg-gray-50/50">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full flex-shrink-0 ${status.color} animate-pulse`} />
          <span className="text-[11px] text-text-muted truncate">{status.label}</span>
        </div>
      </div>
    </aside>
  )
}
