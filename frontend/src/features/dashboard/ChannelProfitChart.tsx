import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { DailyReport } from './api'
import { formatCurrency } from '../../lib/format'

interface ChannelProfitChartProps {
  channels: DailyReport['channels']
}

export function ChannelProfitChart({ channels }: ChannelProfitChartProps) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={channels} layout="vertical" margin={{ top: 10, right: 12, left: 20, bottom: 10 }}>
          <CartesianGrid stroke="#1e293b" horizontal={false} />
          <XAxis
            type="number"
            stroke="#64748b"
            tickLine={false}
            axisLine={false}
            tickFormatter={(value: number) => `${Math.round(value / 1_000_000)}M`}
          />
          <YAxis
            type="category"
            dataKey="channel_name"
            stroke="#64748b"
            tickLine={false}
            axisLine={false}
            width={82}
          />
          <ReferenceLine x={0} stroke="#475569" />
          <Tooltip
            cursor={{ fill: 'rgba(30, 41, 59, 0.45)' }}
            formatter={(value) => [formatCurrency(Number(value)), 'Gross profit']}
            contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 12 }}
          />
          <Bar dataKey="gross_profit" radius={6} maxBarSize={34}>
            {channels.map((channel) => (
              <Cell key={channel.channel} fill={channel.gross_profit >= 0 ? '#34d399' : '#fb7185'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
