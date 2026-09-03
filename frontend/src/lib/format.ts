const currency = new Intl.NumberFormat('vi-VN', {
  style: 'currency',
  currency: 'VND',
  maximumFractionDigits: 0,
})

const integer = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 0 })

export function formatCurrency(value: number): string {
  return currency.format(value)
}

export function formatInteger(value: number): string {
  return integer.format(value)
}

export function formatTimestamp(value: string | null): string {
  if (!value) return '—'
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}
