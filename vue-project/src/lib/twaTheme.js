export function applyTgTheme(tg) {
  if (!tg) return
  const p = tg.themeParams || {}
  const root = document.documentElement
  // Telegram theme params are hex without '#'
  const color = (key, fallback) => (p[key] ? `#${p[key]}` : fallback)
  root.style.setProperty('--tg-bg', color('bg_color', '#ffffff'))
  root.style.setProperty('--tg-text', color('text_color', '#111111'))
  root.style.setProperty('--tg-hint', color('hint_color', '#6b7280'))
  root.style.setProperty('--tg-link', color('link_color', '#1d4ed8'))
  root.style.setProperty('--tg-button', color('button_color', '#1d4ed8'))
  root.style.setProperty('--tg-button-text', color('button_text_color', '#ffffff'))
  root.style.setProperty('--tg-secondary-bg', color('secondary_bg_color', '#f3f4f6'))
}


