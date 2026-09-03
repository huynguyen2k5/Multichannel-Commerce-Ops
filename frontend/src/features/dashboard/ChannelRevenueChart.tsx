import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { DailyReport } from './api'
import { formatCurrency } from '../../lib/format'

const CHANNEL_COLORS: Record<string, string> = {
  shopee: '#f97316',
  tiktok: '#22d3ee',
  website: '#8b5cf6',
}

interface ChannelRevenueChartProps {
  channels: DailyReport['channels']
}

export function ChannelRevenueChart({ channels }: ChannelRevenueChartProps) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={channels} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
          <CartesianGrid stroke="#1e293b" vertical={false} />
          <XAxis dataKey="channel_name" stroke="#64748b" tickLine={false} axisLine={false} />
          <YAxis
            stroke="#64748b"
            tickLine={false}
            axisLine={false}
            tickFormatter={(value: number) => `${Math.round(value / 1_000_000)}M`}
            width={48}
          />
          <Tooltip
            cursor={{ fill: 'rgba(30, 41, 59, 0.45)' }}
            formatter={(value) => [formatCurrency(Number(value)), 'Revenue']}
            contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 12 }}
          />
          <Bar dataKey="revenue" radius={[6, 6, 0, 0]} maxBarSize={64}>
            {channels.map((channel) => (
              <Cell key={channel.channel} fill={CHANNEL_COLORS[channel.channel] ?? '#94a3b8'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
