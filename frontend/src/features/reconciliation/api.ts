import { useQuery } from '@tanstack/react-query'
import { z } from 'zod'

import { apiRequest } from '../../lib/api'

const mismatchSchema = z.object({
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

export function useReconciliations() {
  return useQuery({
    queryKey: ['reconciliations'],
    queryFn: () => apiRequest('/reconciliations', reconciliationListSchema),
  })
}
