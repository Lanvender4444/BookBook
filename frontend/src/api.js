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

  async openBook(id, app = null) {
    const url = app
      ? `${API_BASE}/books/${id}/open?app=${encodeURIComponent(app)}`
      : `${API_BASE}/books/${id}/open`
    const response = await fetch(url, { method: 'POST' })
    return response.json()
  },

  async generateStream(prompt, requirements, onEvent) {
    const response = await fetch(`${API_BASE}/generate/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, requirements })
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
  }
}
