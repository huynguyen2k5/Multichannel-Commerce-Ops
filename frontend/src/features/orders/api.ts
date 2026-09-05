import { useQuery } from '@tanstack/react-query'
import { z } from 'zod'

import { apiRequest } from '../../lib/api'

export const orderSchema = z.object({
  id: z.number(),
  channel_id: z.number(),
  channel: z.string(),
  external_order_id: z.string(),
  order_date: z.string(),
  status: z.string(),
  total_amount: z.coerce.number(),
  source_updated_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})

export const orderItemSchema = z.object({
  id: z.number(),
  product_id: z.number(),
  quantity: z.number(),
  unit_price: z.coerce.number(),
  unit_cost: z.coerce.number(),
  sku: z.string().nullable().optional(),
  product_name: z.string().nullable().optional(),
})

export const orderDetailSchema = orderSchema.extend({
  items: z.array(orderItemSchema),
})

const ordersSchema = z.array(orderSchema)
export type Order = z.infer<typeof orderSchema>
export type OrderItem = z.infer<typeof orderItemSchema>
export type OrderDetail = z.infer<typeof orderDetailSchema>

export interface OrderFilterParams {
  channel?: string
  status?: string
  search?: string
}

export function useOrders(params: OrderFilterParams = {}) {
  const { channel, status, search } = params
  const searchParams = new URLSearchParams({ limit: '100', offset: '0' })
  if (channel && channel !== 'all') {
    searchParams.set('channel', channel)
  }
  if (status && status !== 'all') {
    searchParams.set('status', status)
  }
  if (search && search.trim()) {
    searchParams.set('search', search.trim())
  }

  return useQuery({
    queryKey: ['orders', { channel, status, search }],
    queryFn: () => apiRequest(`/orders?${searchParams.toString()}`, ordersSchema),
  })
}

export function useOrderDetail(orderId: number | null | undefined) {
  return useQuery({
    queryKey: ['orders', orderId],
    queryFn: () => apiRequest(`/orders/${orderId}`, orderDetailSchema),
    enabled: typeof orderId === 'number' && Number.isInteger(orderId) && orderId > 0,
  })
}

