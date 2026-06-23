let API_BASE = (() => {
  const isTauri = typeof window !== 'undefined' && !!(window.__TAURI_INTERNALS__)
  if (isTauri) {
    const port = window.__BOOKBOOK_BACKEND_PORT__ || __BACKEND_PORT__
    return `http://localhost:${port}/api`
  }
  return '/api'
})()

export function setApiBase(base) {
  API_BASE = base
}

export const api = {
  async getBooks() {
    const response = await fetch(`${API_BASE}/books`)
    return response.json()
  },

  async getBook(id) {
    const response = await fetch(`${API_BASE}/books/${id}`)
    return response.json()
  },

  async deleteBook(id) {
    await fetch(`${API_BASE}/books/${id}`, { method: 'DELETE' })
  },

  async exportBook(id, format = 'markdown') {
    const response = await fetch(`${API_BASE}/books/${id}/export?format=${format}`)
    if (format === 'markdown') {
      return response.json()
    }
    return response
  },

  async openBook(id, app = null) {
    const url = app
      ? `${API_BASE}/books/${id}/open?app=${encodeURIComponent(app)}`
      : `${API_BASE}/books/${id}/open`
    const response = await fetch(url, { method: 'POST' })
    return response.json()
  },

  async generateStream(prompt, requirements, onEvent, providerId = null, modelName = null) {
    const body = { prompt, requirements }
    if (providerId) body.provider_id = providerId
    if (modelName) body.model_name = modelName

    const response = await fetch(`${API_BASE}/generate/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            onEvent(data)
          } catch (e) {}
        }
      }
    }
  },

  async getPeers() {
    const response = await fetch(`${API_BASE}/peers`)
    return response.json()
  },

  async syncPeer(peerId) {
    const response = await fetch(`${API_BASE}/peers/${peerId}/sync`, { method: 'POST' })
    return response.json()
  },

  async downloadBook(peerId, bookId) {
    const response = await fetch(`${API_BASE}/peers/${peerId}/books/${bookId}`, { method: 'POST' })
    return response.json()
  },

  async getIdentity() {
    const response = await fetch(`${API_BASE}/identity`)
    return response.json()
  },

  async listProviders() {
    const response = await fetch(`${API_BASE}/providers/list`)
    return response.json()
  },

  async getProvider(providerId) {
    const response = await fetch(`${API_BASE}/providers/${providerId}`)
    return response.json()
  },

  async configureProvider(providerId, apiKey, baseUrl = null, models = null) {
    const body = { provider_id: providerId, api_key: apiKey }
    if (baseUrl) body.base_url = baseUrl
    if (models) body.models = models
    const response = await fetch(`${API_BASE}/providers/configure`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    return response.json()
  },

  async deleteProvider(providerId) {
    const response = await fetch(`${API_BASE}/providers/${providerId}`, { method: 'DELETE' })
    return response.json()
  },

  async setActiveModel(providerId, modelName) {
    const response = await fetch(`${API_BASE}/providers/active`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider_id: providerId, model_name: modelName })
    })
    return response.json()
  },

  async getActiveModel() {
    const response = await fetch(`${API_BASE}/providers/active/detail`)
    return response.json()
  },

  async testProvider(providerId) {
    const response = await fetch(`${API_BASE}/providers/${providerId}/test`, { method: 'POST' })
    return response.json()
  },

  async migrateEnvKeys() {
    const response = await fetch(`${API_BASE}/providers/migrate-env`, { method: 'POST' })
    return response.json()
  },

  // ---------------- 知识源 (RAG) ----------------

  async listSources(category = null) {
    const url = category
      ? `${API_BASE}/knowledge/sources?category=${category}`
      : `${API_BASE}/knowledge/sources`
    const response = await fetch(url)
    return response.json()
  },

  async uploadSource(file, category, { name = '', prompt = '', language = '' } = {}) {
    const form = new FormData()
    form.append('file', file)
    form.append('category', category)
    if (name) form.append('name', name)
    if (prompt) form.append('prompt', prompt)
    if (language) form.append('language', language)
    const response = await fetch(`${API_BASE}/knowledge/sources/upload`, {
      method: 'POST',
      body: form
    })
    if (!response.ok) throw new Error((await response.json()).detail || 'upload failed')
    return response.json()
  },

  async linkSource(path, category, { name = '', prompt = '', language = '' } = {}) {
    const response = await fetch(`${API_BASE}/knowledge/sources/link`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path, category, name, prompt, language })
    })
    if (!response.ok) throw new Error((await response.json()).detail || 'link failed')
    return response.json()
  },

  async createTextSource(name, category, content, { prompt = '', language = '' } = {}) {
    const response = await fetch(`${API_BASE}/knowledge/sources/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, category, content, prompt, language })
    })
    if (!response.ok) throw new Error((await response.json()).detail || 'create failed')
    return response.json()
  },

  async updateSource(id, patch) {
    const response = await fetch(`${API_BASE}/knowledge/sources/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch)
    })
    return response.json()
  },

  async deleteSource(id) {
    const response = await fetch(`${API_BASE}/knowledge/sources/${id}`, { method: 'DELETE' })
    if (!response.ok) throw new Error((await response.json()).detail || 'delete failed')
    return response.json()
  },

  async reindexSource(id) {
    const response = await fetch(`${API_BASE}/knowledge/sources/${id}/reindex`, { method: 'POST' })
    return response.json()
  },

  // ---------------- 写作卡 ----------------

  async listCards() {
    const response = await fetch(`${API_BASE}/knowledge/cards`)
    return response.json()
  },

  async createCard(card) {
    const response = await fetch(`${API_BASE}/knowledge/cards`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(card)
    })
    if (!response.ok) throw new Error((await response.json()).detail || 'create failed')
    return response.json()
  },

  async updateCard(id, card) {
    const response = await fetch(`${API_BASE}/knowledge/cards/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(card)
    })
    if (!response.ok) throw new Error((await response.json()).detail || 'update failed')
    return response.json()
  },

  async deleteCard(id) {
    const response = await fetch(`${API_BASE}/knowledge/cards/${id}`, { method: 'DELETE' })
    if (!response.ok) throw new Error((await response.json()).detail || 'delete failed')
    return response.json()
  },

  async duplicateCard(id) {
    const response = await fetch(`${API_BASE}/knowledge/cards/${id}/duplicate`, { method: 'POST' })
    return response.json()
  },

  // ---------------- 设置：web 搜索 ----------------

  async getSearchConfig() {
    const response = await fetch(`${API_BASE}/settings/search`)
    return response.json()
  },

  async setSearchConfig({ provider, api_key }) {
    const body = { provider }
    if (api_key !== undefined) body.api_key = api_key
    const response = await fetch(`${API_BASE}/settings/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    return response.json()
  },
}