import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'

import { apiRequest } from '../../lib/api'

export const alertSchema = z.object({
  id: z.number(),
  type: z.enum(['low_stock', 'reconciliation_mismatch', 'sync_failure']),
  severity: z.enum(['info', 'warning', 'critical']),
  dedup_key: z.string(),
  message: z.string(),
  resolved: z.boolean(),
  created_at: z.string(),
  resolved_at: z.string().nullable(),
  notified_at: z.string().nullable(),
})

const alertsSchema = z.array(alertSchema)
export type Alert = z.infer<typeof alertSchema>

export function useAlerts(resolved?: boolean) {
  return useQuery({
    queryKey: ['alerts', { resolved }],
    queryFn: ({ signal }) => {
      const query = resolved !== undefined ? `?resolved=${String(resolved)}` : ''
      return apiRequest(`/alerts${query}`, alertsSchema, { signal })
    },
  })
}

export function useResolveAlert() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (alertId: number) =>
      apiRequest(`/alerts/${alertId}/resolve`, alertSchema, { method: 'PATCH' }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['alerts'] })
      await queryClient.invalidateQueries({ queryKey: ['inventory'] })
    },
  })
}
