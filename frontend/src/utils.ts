export function formatVND(amount: number, compact = false): string {
  const sign = amount < 0 ? "-" : ""
  const abs = Math.abs(amount)
  if (compact) {
    if (abs >= 1_000_000_000) return `${sign}₫${(abs / 1_000_000_000).toFixed(1)}B`
    if (abs >= 1_000_000) return `${sign}₫${(abs / 1_000_000).toFixed(1)}M`
    if (abs >= 1_000) return `${sign}₫${(abs / 1_000).toFixed(0)}K`
    return `${sign}₫${abs.toLocaleString("vi-VN")}`
  }
  return `${sign}₫${abs.toLocaleString("vi-VN")}`
}

export function formatCurrency(amount: number, currency = "VND"): string {
  if (currency === "VND") {
    return formatVND(amount)
  }
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency }).format(amount)
}

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return dateStr
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })
}

export function formatDateTime(dateStr: string): string {
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return dateStr
  const date = d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })
  const time = d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })
  return `${date}, ${time}`
}

export const CHANNEL_COLORS: Record<string, string> = {
  shopee: "#F97316",
  tiktok: "#27272A",
  website: "#4F46E5",
}

export const CHANNEL_LABELS: Record<string, string> = {
  shopee: "Shopee",
  tiktok: "TikTok Shop",
  website: "Website",
}
