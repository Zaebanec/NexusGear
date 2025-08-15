function getCloud(tg) {
  const webApp = tg || (typeof window !== 'undefined' ? /** @type {any} */ (window).Telegram?.WebApp : null)
  return webApp?.CloudStorage || null
}

export function isCloudAvailable(tg) {
  return !!getCloud(tg)
}

export function getItem(key, tg) {
  const cloud = getCloud(tg)
  if (!cloud) return Promise.resolve(null)
  return new Promise((resolve) => {
    try {
      cloud.getItem(key, (err, value) => {
        if (err) return resolve(null)
        resolve(value ?? null)
      })
    } catch {
      resolve(null)
    }
  })
}

export function setItem(key, value, tg) {
  const cloud = getCloud(tg)
  if (!cloud) return Promise.resolve(false)
  return new Promise((resolve) => {
    try {
      cloud.setItem(key, value, (err) => {
        resolve(!err)
      })
    } catch {
      resolve(false)
    }
  })
}


