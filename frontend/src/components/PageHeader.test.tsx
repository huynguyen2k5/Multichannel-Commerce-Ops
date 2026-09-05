import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { PageHeader } from './PageHeader'

describe('PageHeader', () => {
  it('renders title correctly', () => {
    render(<PageHeader title="Orders Management" />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Orders Management')
  })

  it('renders subtitle or description when provided', () => {
    const { rerender } = render(
      <PageHeader title="Orders" subtitle="Track and manage live orders" />
    )
    expect(screen.getByText('Track and manage live orders')).toBeInTheDocument()

    rerender(<PageHeader title="Orders" description="Detailed description" />)
    expect(screen.getByText('Detailed description')).toBeInTheDocument()
  })

  it('renders eyebrow when provided', () => {
    render(<PageHeader title="Overview" eyebrow="System Health" />)
    expect(screen.getByText('System Health')).toBeInTheDocument()
  })

  it('renders action elements when provided', () => {
    render(
      <PageHeader
        title="Inventory"
        action={<button type="button">Sync Stock</button>}
      />
    )
    expect(screen.getByRole('button', { name: 'Sync Stock' })).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      <PageHeader title="Test" className="custom-test-class" />
    )
    expect(container.firstChild).toHaveClass('custom-test-class')
  })
})
