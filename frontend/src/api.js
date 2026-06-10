const API_BASE = '/api'

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
}