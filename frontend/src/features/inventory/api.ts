import { useQuery } from '@tanstack/react-query'
import { z } from 'zod'

import { apiRequest } from '../../lib/api'

const inventorySchema = z.array(
  z.object({
    product_id: z.number(),
    sku: z.string(),
    name: z.string(),
    cost_price: z.coerce.number(),
    current_stock: z.number(),
    reorder_threshold: z.number(),
    is_low_stock: z.boolean(),
  }),
)

export type InventoryItem = z.infer<typeof inventorySchema>[number]

export function useInventory() {
  return useQuery({
    queryKey: ['inventory'],
    queryFn: ({ signal }) => apiRequest('/inventory', inventorySchema, { signal }),
  })
}
