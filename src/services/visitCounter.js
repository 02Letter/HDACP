const STORAGE_KEY = 'hdacp-visitor-v1'
const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

export function browserIdentifier(storage, cryptoApi) {
  try {
    const previous = storage.getItem(STORAGE_KEY)
    if (UUID_V4.test(previous || '')) return previous
    const identifier = cryptoApi.randomUUID()
    storage.setItem(STORAGE_KEY, identifier)
    // If storage is unavailable, avoid counting the same browser again on refresh.
    return storage.getItem(STORAGE_KEY) === identifier ? identifier : null
  } catch {
    return null
  }
}

export async function fetchVisitorCount(endpoint, { storage, cryptoApi, fetchApi = fetch }) {
  const identifier = browserIdentifier(storage, cryptoApi)
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 8000)
  try {
    const response = await fetchApi(endpoint, {
      method: identifier ? 'POST' : 'GET',
      ...(identifier ? { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ browserId: identifier }) } : {}),
      signal: controller.signal,
      credentials: 'omit',
      cache: 'no-store'
    })
    if (!response.ok) throw new Error('Visitor counter unavailable')
    const { count } = await response.json()
    if (!Number.isSafeInteger(count) || count < 0) throw new Error('Invalid visitor count')
    return count
  } finally {
    clearTimeout(timer)
  }
}
