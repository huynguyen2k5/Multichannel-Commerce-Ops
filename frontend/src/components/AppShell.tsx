import type { PropsWithChildren } from 'react'
import { NavLink } from 'react-router-dom'

const links = [
  ['/', 'Dashboard'],
  ['/orders', 'Orders'],
  ['/inventory', 'Inventory'],
  ['/alerts', 'Alerts'],
  ['/reconciliation', 'Reconciliation'],
] as const

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[240px_1fr]">
      <aside className="border-b border-slate-800 bg-slate-950/90 px-5 py-5 lg:min-h-screen lg:border-b-0 lg:border-r">
        <div className="mb-6">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-400">MCO</p>
          <h1 className="mt-1 text-lg font-semibold text-white">Commerce Operations</h1>
          <p className="mt-1 text-xs text-slate-500">Operational control plane</p>
        </div>
        <nav className="flex gap-2 overflow-x-auto lg:flex-col">
          {links.map(([to, label]) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `whitespace-nowrap rounded-lg px-3 py-2 text-sm transition ${
                  isActive
                    ? 'bg-cyan-500/15 font-medium text-cyan-300 ring-1 ring-cyan-500/20'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-slate-100'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="min-w-0 p-4 sm:p-6 lg:p-8">{children}</main>
    </div>
  )
}
