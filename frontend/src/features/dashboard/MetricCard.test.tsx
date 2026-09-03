import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { MetricCard } from './MetricCard'

describe('MetricCard', () => {
  it('renders operational label and value', () => {
    render(<MetricCard label="Revenue" value="₫24,500,000" hint="Today" />)

    expect(screen.getByText('Revenue')).toBeInTheDocument()
    expect(screen.getByText('₫24,500,000')).toBeInTheDocument()
    expect(screen.getByText('Today')).toBeInTheDocument()
  })
})
