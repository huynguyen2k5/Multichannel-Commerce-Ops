import { AsyncState } from '../components/AsyncState'
import { PageHeader } from '../components/PageHeader'
import { Panel } from '../components/Panel'
import { useOrders } from '../features/orders/api'
import { formatCurrency, formatTimestamp } from '../lib/format'

const channelClass: Record<string, string> = {
  shopee: 'bg-orange-500/10 text-orange-300',
  tiktok: 'bg-cyan-500/10 text-cyan-300',
  website: 'bg-violet-500/10 text-violet-300',
}

export function OrdersPage() {
  const query = useOrders()

  return (
    <>
      <PageHeader
        eyebrow="Normalized data"
        title="Orders"
        description="Imported channel orders after validation and idempotency checks. Repeated source deliveries remain a no-op."
      />
      <AsyncState isLoading={query.isLoading} error={query.error}>
        <Panel title="Recent orders" subtitle={`${query.data?.length ?? 0} order(s) loaded`}>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="text-xs uppercase tracking-wider text-slate-500">
                <tr className="border-b border-slate-800">
                  <th className="pb-3 font-medium">Channel</th>
                  <th className="pb-3 font-medium">External ID</th>
                  <th className="pb-3 font-medium">Order date</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 text-right font-medium">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {query.data?.map((order) => (
                  <tr key={order.id} className="text-slate-300">
                    <td className="py-3">
                      <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${channelClass[order.channel] ?? 'bg-slate-800 text-slate-300'}`}>
                        {order.channel}
                      </span>
                    </td>
                    <td className="py-3 font-medium text-slate-100">{order.external_order_id}</td>
                    <td className="py-3 text-slate-400">{formatTimestamp(order.order_date)}</td>
                    <td className="py-3 text-emerald-300">{order.status}</td>
                    <td className="py-3 text-right font-medium text-slate-100">{formatCurrency(order.total_amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!query.data?.length ? <p className="py-8 text-center text-sm text-slate-500">No orders imported yet.</p> : null}
          </div>
        </Panel>
      </AsyncState>
    </>
  )
}
