export function digitsOnly(value) {
  return String(value || '').replace(/\D+/g, '')
}

export function normalizeRuPhone(value) {
  // Возвращает 11 цифр, первая 7. Принимает 8/7/9*** и т.п.
  const d = digitsOnly(value)
  if (!d) return ''
  let n = d
  if (n.length === 11 && (n.startsWith('7') || n.startsWith('8'))) {
    n = '7' + n.slice(1)
  } else if (n.length === 10 && n.startsWith('9')) {
    n = '7' + n
  } else if (n.length > 11) {
    n = n.slice(0, 11)
    if (n.startsWith('8')) n = '7' + n.slice(1)
  }
  return n
}

export function maskRuPhone(value) {
  const n = normalizeRuPhone(value)
  if (!n) return ''
  const a = n.padEnd(11, '_').split('')
  // +7 (XXX) XXX-XX-XX
  return `+7 (${a[1]}${a[2]}${a[3]}) ${a[4]}${a[5]}${a[6]}-${a[7]}${a[8]}-${a[9]}${a[10]}`.replace(/_/g, '')
}

export function isValidRuPhone(value) {
  const n = normalizeRuPhone(value)
  return n.length === 11 && n.startsWith('7')
}


