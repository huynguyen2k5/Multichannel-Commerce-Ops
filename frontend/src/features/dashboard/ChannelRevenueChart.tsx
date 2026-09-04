import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { DailyReport } from './api'
import { CHANNEL_COLORS, CHANNEL_LABELS, formatVND } from '../../utils'

interface ChannelRevenueChartProps {
  channels: DailyReport['channels']
}

interface TooltipPayloadItem {
  name: string
  value: number
  fill?: string
}

interface RevenueTooltipProps {
  active?: boolean
  payload?: TooltipPayloadItem[]
  label?: string
}

function RevenueTooltip({ active, payload, label }: RevenueTooltipProps) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-border rounded-lg shadow-md px-3 py-2.5 text-xs">
      <p className="font-semibold text-gray-800 mb-1.5">{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2 text-gray-600">
          <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: p.fill }} />
          <span>Revenue: {formatVND(p.value, true)}</span>
        </div>
      ))}
    </div>
  )
}

export function ChannelRevenueChart({ channels }: ChannelRevenueChartProps) {
  const chartData = channels.map((c) => ({
    name: CHANNEL_LABELS[c.channel] ?? c.channel_name,
    revenue: c.revenue,
    channel: c.channel,
  }))

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }} barSize={32}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E4E7EC" vertical={false} />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11, fill: '#667085' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(v: number) => formatVND(v, true)}
            tick={{ fontSize: 10, fill: '#9CA3AF' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<RevenueTooltip />} cursor={{ fill: '#F7F8FA' }} />
          <Bar dataKey="revenue" radius={[4, 4, 0, 0]} name="Revenue">
            {chartData.map((entry) => (
              <Cell key={entry.channel} fill={CHANNEL_COLORS[entry.channel] ?? '#94A3B8'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

