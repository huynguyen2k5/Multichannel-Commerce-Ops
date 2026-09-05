import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { DailyReport } from './api'
import { CHANNEL_LABELS, formatVND } from '../../utils'

interface ChannelProfitChartProps {
  channels: DailyReport['channels']
}

interface ProfitPayloadItem {
  value: number
}

interface ProfitTooltipProps {
  active?: boolean
  payload?: ProfitPayloadItem[]
  label?: string
}

function ProfitTooltip({ active, payload, label }: ProfitTooltipProps) {
  if (!active || !payload?.length) return null
  const val = payload[0]?.value ?? 0
  return (
    <div className="bg-white border border-border rounded-lg shadow-md px-3 py-2.5 text-xs">
      <p className="font-semibold text-gray-800 mb-1">{label}</p>
      <p className={val >= 0 ? 'text-success-600 font-semibold' : 'text-critical-600 font-semibold'}>
        Profit: {formatVND(val, true)}
      </p>
    </div>
  )
}

export function ChannelProfitChart({ channels }: ChannelProfitChartProps) {
  const chartData = channels.map((c) => ({
    name: CHANNEL_LABELS[c.channel] ?? c.channel_name,
    gross_profit: c.gross_profit,
    channel: c.channel,
  }))

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 4, right: 24, left: 0, bottom: 0 }}
          barSize={20}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E4E7EC" horizontal={false} />
          <XAxis
            type="number"
            tickFormatter={(v: number) => formatVND(v, true)}
            tick={{ fontSize: 10, fill: '#9CA3AF' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 11, fill: '#667085' }}
            axisLine={false}
            tickLine={false}
            width={80}
          />
          <Tooltip content={<ProfitTooltip />} cursor={{ fill: '#F7F8FA' }} />
          <ReferenceLine x={0} stroke="#E4E7EC" strokeWidth={1} />
          <Bar dataKey="gross_profit" radius={[0, 3, 3, 0]} name="Gross Profit">
            {chartData.map((entry) => (
              <Cell
                key={entry.channel}
                fill={entry.gross_profit >= 0 ? '#16A34A' : '#DC2626'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

