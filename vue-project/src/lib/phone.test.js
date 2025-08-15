import { describe, it, expect } from 'vitest'
import { digitsOnly, normalizeRuPhone, maskRuPhone, isValidRuPhone } from './phone.js'

describe('phone utils', () => {
  it('digitsOnly', () => {
    expect(digitsOnly('+7 (999) 123-45-67')).toBe('79991234567')
    expect(digitsOnly('abc')).toBe('')
  })

  it('normalizeRuPhone', () => {
    expect(normalizeRuPhone('+7 (999) 123-45-67')).toBe('79991234567')
    expect(normalizeRuPhone('8 (999) 123-45-67')).toBe('79991234567')
    expect(normalizeRuPhone('9991234567')).toBe('79991234567')
  })

  it('maskRuPhone', () => {
    expect(maskRuPhone('79991234567')).toContain('+7 (999) 123-45-67')
  })

  it('isValidRuPhone', () => {
    expect(isValidRuPhone('79991234567')).toBe(true)
    // 8*** нормализуется в 7*** и считается валидным
    expect(isValidRuPhone('89991234567')).toBe(true)
    expect(isValidRuPhone('7999123456')).toBe(false)
  })
})


