import assert from 'node:assert/strict'
import { test } from 'node:test'
import { browserIdentifier, fetchVisitorCount } from '../src/services/visitCounter.js'

const id = 'bedffad6-1337-48ca-952b-03e17cdb9251'
const cryptoApi = { randomUUID: () => id }
const memoryStorage = () => {
  const values = new Map()
  return { getItem: key => values.get(key) || null, setItem: (key, value) => values.set(key, value) }
}

test('browser identity persists across page loads', () => {
  const storage = memoryStorage()
  assert.equal(browserIdentifier(storage, cryptoApi), id)
  assert.equal(browserIdentifier(storage, { randomUUID: () => { throw new Error('should reuse identity') } }), id)
})

test('blocked storage only reads shared total', async () => {
  let method
  const count = await fetchVisitorCount('https://www.xcfqms.com/hdacp-visits/api/visits', {
    storage: { getItem: () => { throw new Error('blocked') } }, cryptoApi,
    fetchApi: async (_, options) => { method = options.method; return { ok: true, json: async () => ({ count: 12 }) } }
  })
  assert.equal(method, 'GET')
  assert.equal(count, 12)
})

test('stored browser ID is sent to server and total is read', async () => {
  const count = await fetchVisitorCount('https://www.xcfqms.com/hdacp-visits/api/visits', {
    storage: memoryStorage(), cryptoApi,
    fetchApi: async (_, options) => {
      assert.equal(options.method, 'POST')
      assert.deepEqual(JSON.parse(options.body), { browserId: id })
      return { ok: true, json: async () => ({ count: 23 }) }
    }
  })
  assert.equal(count, 23)
})

test('invalid server response cannot become a displayed count', async () => {
  await assert.rejects(fetchVisitorCount('https://www.xcfqms.com/hdacp-visits/api/visits', {
    storage: memoryStorage(), cryptoApi,
    fetchApi: async () => ({ ok: true, json: async () => ({ count: -1 }) })
  }))
})
