import { describe, expect, it } from 'vitest'

import { formatInteger, formatVND } from '../utils'

describe('format utils', () => {
  it('formats counts without decimal noise', () => {
    expect(formatInteger(1200)).toMatch(/1[.,]200|1\s?200/)
  })

  it('formats VND currency accurately', () => {
    expect(formatVND(500000)).toContain('500')
    expect(formatVND(1500000, true)).toBe('₫1.5M')
  })
})
