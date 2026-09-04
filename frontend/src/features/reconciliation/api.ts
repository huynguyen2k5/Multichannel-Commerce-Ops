import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'

import { apiRequest } from '../../lib/api'

export const mismatchSchema = z.object({
  external_order_id: z.string(),
  code: z.string(),
  expected: z.string().nullable().optional(),
  actual: z.string().nullable().optional(),
})

export const reconciliationSchema = z.object({
  id: z.number(),
  source_system: z.string(),
  status: z.enum(['success', 'mismatch', 'failed']),
  records_checked: z.number(),
  mismatches_found: z.number(),
  detail_json: z.object({ mismatches: z.array(mismatchSchema).default([]) }).passthrough(),
  started_at: z.string(),
  completed_at: z.string(),
})

const reconciliationListSchema = z.array(reconciliationSchema)
export type Reconciliation = z.infer<typeof reconciliationSchema>
export type ReconciliationMismatch = z.infer<typeof mismatchSchema>

export function useReconciliations() {
  return useQuery({
    queryKey: ['reconciliations'],
    queryFn: () => apiRequest('/reconciliations', reconciliationListSchema),
  })
}

export function useReconciliation(id?: number) {
  return useQuery({
    queryKey: ['reconciliations', id],
    queryFn: () => apiRequest(`/reconciliations/${id}`, reconciliationSchema),
    enabled: typeof id === 'number' && !isNaN(id),
  })
}

export interface RunReconciliationPayload {
  source_system: string
  orders: Array<{
    external_order_id: string
    total_amount: number
  }>
}

export function useRunReconciliation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: RunReconciliationPayload) =>
      apiRequest('/reconciliations', reconciliationSchema, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['reconciliations'] })
      await queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })
}
