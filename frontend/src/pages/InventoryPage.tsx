import { AsyncState } from '../components/AsyncState'
import { PageHeader } from '../components/PageHeader'
import { Panel } from '../components/Panel'
import { useInventory } from '../features/inventory/api'
import { formatCurrency } from '../lib/format'

export function InventoryPage() {
  const query = useInventory()
  const lowStock = query.data?.filter((item) => item.is_low_stock).length ?? 0

  return (
    <>
      <PageHeader
        eyebrow="Stock control"
        title="Inventory"
        description="Current stock is updated atomically during order import. Threshold breaches become operational alerts."
      />
      <AsyncState isLoading={query.isLoading} error={query.error}>
        <Panel title="Inventory status" subtitle={`${lowStock} SKU(s) need attention`}>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="text-xs uppercase tracking-wider text-slate-500">
                <tr className="border-b border-slate-800">
                  <th className="pb-3 font-medium">SKU</th>
                  <th className="pb-3 font-medium">Product</th>
                  <th className="pb-3 text-right font-medium">Cost</th>
                  <th className="pb-3 text-right font-medium">Stock</th>
                  <th className="pb-3 text-right font-medium">Threshold</th>
                  <th className="pb-3 text-right font-medium">Health</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {query.data?.map((item) => (
                  <tr key={item.product_id} className="text-slate-300">
                    <td className="py-3 font-medium text-slate-100">{item.sku}</td>
                    <td className="py-3 text-slate-400">{item.name}</td>
                    <td className="py-3 text-right">{formatCurrency(item.cost_price)}</td>
                    <td className="py-3 text-right font-semibold text-slate-100">{item.current_stock}</td>
                    <td className="py-3 text-right text-slate-500">{item.reorder_threshold}</td>
                    <td className="py-3 text-right">
                      <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${item.is_low_stock ? 'bg-amber-500/10 text-amber-300' : 'bg-emerald-500/10 text-emerald-300'}`}>
                        {item.is_low_stock ? 'Low stock' : 'Healthy'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </AsyncState>
    </>
  )
}
