import { describe, expect, it } from 'vitest'

import { formatInteger } from './format'

describe('formatInteger', () => {
  it('formats counts without decimal noise', () => {
    expect(formatInteger(1200)).toMatch(/1[.,]200|1\s?200/)
  })
})
