import React, { Component, type ReactNode } from 'react'
import { ErrorState } from './ErrorState'

export interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode | ((error: Error, reset: () => void) => ReactNode)
  onReset?: () => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  override componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('Uncaught application error:', error, errorInfo)
  }

  resetErrorBoundary = (): void => {
    this.props.onReset?.()
    this.setState({ hasError: false, error: null })
  }

  override render(): ReactNode {
    if (this.state.hasError && this.state.error) {
      if (typeof this.props.fallback === 'function') {
        return this.props.fallback(this.state.error, this.resetErrorBoundary)
      }
      if (this.props.fallback) {
        return this.props.fallback
      }
      return (
        <div className="p-6 max-w-[1440px] w-full">
          <ErrorState
            title="Something went wrong"
            description={this.state.error.message || 'An unexpected rendering error occurred.'}
            onRetry={this.resetErrorBoundary}
          />
        </div>
      )
    }

    return this.props.children
  }
}
