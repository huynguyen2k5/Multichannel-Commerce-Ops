import type { PropsWithChildren, ReactNode } from 'react'

interface PanelProps extends PropsWithChildren {
  title: string
  subtitle?: string
  action?: ReactNode
}

export function Panel({ title, subtitle, action, children }: PanelProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/65 shadow-2xl shadow-black/10">
      <div className="flex items-start justify-between gap-4 border-b border-slate-800 px-5 py-4">
        <div>
          <h3 className="font-medium text-slate-100">{title}</h3>
          {subtitle ? <p className="mt-1 text-xs text-slate-500">{subtitle}</p> : null}
        </div>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
  )
}
