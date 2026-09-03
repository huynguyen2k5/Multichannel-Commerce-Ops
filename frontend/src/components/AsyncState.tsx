import type { PropsWithChildren } from 'react'

import { ApiError } from '../lib/api'

interface AsyncStateProps extends PropsWithChildren {
  isLoading: boolean
  error: unknown
}

export function AsyncState({ isLoading, error, children }: AsyncStateProps) {
  if (isLoading) {
    return <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 text-sm text-slate-400">Loading…</div>
  }
  if (error) {
    const message = error instanceof ApiError ? `${error.code}: ${error.message}` : 'Unable to load data.'
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
        {message}
      </div>
    )
  }
  return children
}
