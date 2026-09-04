import { useMemo, type PropsWithChildren } from 'react'

import { Sidebar } from './Sidebar'
import { ToastProvider } from './Toast'
import { useAlerts } from '../features/alerts/api'

export function AppShell({ children }: PropsWithChildren) {
  const { data: activeAlertsList } = useAlerts(false)

  const alertCounts = useMemo(() => {
    if (!activeAlertsList) return undefined
    const critical = activeAlertsList.filter((a) => a.severity === 'critical').length
    const warning = activeAlertsList.filter((a) => a.severity === 'warning').length
    return { critical, warning, total: activeAlertsList.length }
  }, [activeAlertsList])

  return (
    <ToastProvider>
      <div className="flex h-screen overflow-hidden bg-[#F7F8FA] font-sans antialiased text-gray-900">
        <Sidebar activeAlerts={alertCounts} />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </ToastProvider>
  )
}


