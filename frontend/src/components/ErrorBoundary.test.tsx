import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { ErrorBoundary } from './ErrorBoundary'

function BrokenComponent({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test rendering crash')
  }
  return <div>Healthy content</div>
}

describe('ErrorBoundary', () => {
  it('renders children normally when there is no error', () => {
    render(
      <ErrorBoundary>
        <BrokenComponent shouldThrow={false} />
      </ErrorBoundary>,
    )

    expect(screen.getByText('Healthy content')).toBeInTheDocument()
  })

  it('catches render error and displays ErrorState fallback', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <BrokenComponent shouldThrow={true} />
      </ErrorBoundary>,
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('Test rendering crash')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()

    consoleSpy.mockRestore()
  })

  it('supports custom function fallback', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary
        fallback={(err, reset) => (
          <div>
            <p>Custom Error: {err.message}</p>
            <button type="button" onClick={reset}>
              Custom Reset
            </button>
          </div>
        )}
      >
        <BrokenComponent shouldThrow={true} />
      </ErrorBoundary>,
    )

    expect(screen.getByText('Custom Error: Test rendering crash')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Custom Reset' })).toBeInTheDocument()

    consoleSpy.mockRestore()
  })

  it('calls onReset callback when retrying', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const onReset = vi.fn()

    render(
      <ErrorBoundary onReset={onReset}>
        <BrokenComponent shouldThrow={true} />
      </ErrorBoundary>,
    )

    const retryBtn = screen.getByRole('button', { name: /retry/i })
    fireEvent.click(retryBtn)

    expect(onReset).toHaveBeenCalledTimes(1)

    consoleSpy.mockRestore()
  })
})
