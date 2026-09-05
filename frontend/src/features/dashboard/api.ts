import { useQuery } from '@tanstack/react-query'
import { z } from 'zod'

import { apiRequest } from '../../lib/api'

const money = z.coerce.number()

export const dailyReportSchema = z.object({
  date: z.string(),
  totals: z.object({
    orders: z.number(),
    revenue: money,
    cogs: money,
    gross_profit: money,
  }),
  channels: z.array(
    z.object({
      channel: z.string(),
      channel_name: z.string(),
      orders: z.number(),
      revenue: money,
      cogs: money,
      gross_profit: money,
    }),
  ),
})

export type DailyReport = z.infer<typeof dailyReportSchema>

export function useDailyReport(date?: string) {
  const path = date ? `/reports/daily?date=${encodeURIComponent(date)}` : '/reports/daily'
  return useQuery({
    queryKey: ['reports', 'daily', date ?? 'latest'],
    queryFn: ({ signal }) => apiRequest(path, dailyReportSchema, { signal }),
  })
}

