import { useQuery } from '@tanstack/react-query'
import { z } from 'zod'

import { apiRequest } from '../../lib/api'

export const orderSchema = z.object({
  id: z.number(),
  channel_id: z.number(),
  channel: z.string(),
  external_order_id: z.string(),
  order_date: z.string(),
  status: z.literal('paid'),
  total_amount: z.coerce.number(),
  source_updated_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})

const ordersSchema = z.array(orderSchema)
export type Order = z.infer<typeof orderSchema>

export function useOrders() {
  return useQuery({
    queryKey: ['orders'],
    queryFn: () => apiRequest('/orders?limit=100&offset=0', ordersSchema),
  })
}
