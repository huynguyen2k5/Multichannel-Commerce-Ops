import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import {
  AlertStatusBadge,
  Badge,
  ChannelBadge,
  InventoryStatusBadge,
  OrderStatusBadge,
  ReconciliationStatusBadge,
  SeverityBadge,
} from './Badge'

describe('Badge Components', () => {
  describe('Badge', () => {
    it('renders with default variant and size', () => {
      render(<Badge>Default Badge</Badge>)
      const el = screen.getByText('Default Badge')
      expect(el).toBeInTheDocument()
      expect(el).toHaveClass('bg-gray-100')
      expect(el).toHaveClass('px-2')
    })

    it('renders with specific variant and size', () => {
      render(
        <Badge variant="critical" size="sm">
          Critical Badge
        </Badge>
      )
      const el = screen.getByText('Critical Badge')
      expect(el).toHaveClass('bg-critical-50')
      expect(el).toHaveClass('px-1.5')
    })
  })

  describe('SeverityBadge', () => {
    it('renders normalized labels for severities', () => {
      const { rerender } = render(<SeverityBadge severity="critical" />)
      expect(screen.getByText('CRITICAL')).toBeInTheDocument()

      rerender(<SeverityBadge severity="WARNING" />)
      expect(screen.getByText('WARNING')).toBeInTheDocument()

      rerender(<SeverityBadge severity="info" />)
      expect(screen.getByText('INFO')).toBeInTheDocument()
    })

    it('handles unknown severity gracefully', () => {
      render(<SeverityBadge severity="unknown" />)
      expect(screen.getByText('UNKNOWN')).toBeInTheDocument()
    })
  })

  describe('AlertStatusBadge', () => {
    it('renders Active for active status', () => {
      render(<AlertStatusBadge status="active" />)
      expect(screen.getByText('Active')).toBeInTheDocument()
    })

    it('renders Resolved for resolved status', () => {
      render(<AlertStatusBadge status="resolved" />)
      expect(screen.getByText('Resolved')).toBeInTheDocument()
    })
  })

  describe('OrderStatusBadge', () => {
    it('renders proper badge for order statuses', () => {
      const { rerender } = render(<OrderStatusBadge status="paid" />)
      expect(screen.getByText('Paid')).toBeInTheDocument()

      rerender(<OrderStatusBadge status="completed" />)
      expect(screen.getByText('Completed')).toBeInTheDocument()

      rerender(<OrderStatusBadge status="processing" />)
      expect(screen.getByText('Processing')).toBeInTheDocument()

      rerender(<OrderStatusBadge status="pending" />)
      expect(screen.getByText('Pending')).toBeInTheDocument()

      rerender(<OrderStatusBadge status="cancelled" />)
      expect(screen.getByText('Cancelled')).toBeInTheDocument()
    })

    it('handles unexpected order status', () => {
      render(<OrderStatusBadge status="refunded" />)
      expect(screen.getByText('refunded')).toBeInTheDocument()
    })
  })

  describe('ChannelBadge', () => {
    it('renders channel labels correctly', () => {
      render(<ChannelBadge channel="shopee" />)
      expect(screen.getByText('Shopee')).toBeInTheDocument()
    })

    it('renders unknown channel with original name', () => {
      render(<ChannelBadge channel="CustomShop" />)
      expect(screen.getByText('CustomShop')).toBeInTheDocument()
    })
  })

  describe('ReconciliationStatusBadge', () => {
    it('renders known reconciliation status labels', () => {
      const { rerender } = render(<ReconciliationStatusBadge status="success" />)
      expect(screen.getByText('Success')).toBeInTheDocument()

      rerender(<ReconciliationStatusBadge status="mismatch" />)
      expect(screen.getByText('Mismatch')).toBeInTheDocument()

      rerender(<ReconciliationStatusBadge status="failed" />)
      expect(screen.getByText('Failed')).toBeInTheDocument()

      rerender(<ReconciliationStatusBadge status="running" />)
      expect(screen.getByText('Running')).toBeInTheDocument()
    })
  })

  describe('InventoryStatusBadge', () => {
    it('renders known inventory status labels', () => {
      const { rerender } = render(<InventoryStatusBadge status="healthy" />)
      expect(screen.getByText('Healthy')).toBeInTheDocument()

      rerender(<InventoryStatusBadge status="low" />)
      expect(screen.getByText('Low Stock')).toBeInTheDocument()

      rerender(<InventoryStatusBadge status="out" />)
      expect(screen.getByText('Out of Stock')).toBeInTheDocument()
    })
  })
})
