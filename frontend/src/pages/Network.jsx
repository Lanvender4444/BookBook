import { useEffect, useState } from 'react'
import PeerList from '../components/PeerList'

function Network() {
  const [peers, setPeers] = useState([])
  const [selectedPeer, setSelectedPeer] = useState(null)
  const [peerBooks, setPeerBooks] = useState([])

  useEffect(() => {
    fetchPeers()
    const interval = setInterval(fetchPeers, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchPeers = async () => {
    try {
      const response = await fetch('/api/peers')
      const data = await response.json()
      setPeers(data)
    } catch (error) {
      console.error('Error fetching peers:', error)
    }
  }

  const handleSyncPeer = async (peerId) => {
    try {
      const response = await fetch(`/api/peers/${peerId}/sync`, { method: 'POST' })
      const data = await response.json()
      setSelectedPeer(peerId)
      setPeerBooks(data.books || [])
    } catch (error) {
      console.error('Error syncing peer:', error)
    }
  }

  const handleDownloadBook = async (peerId, bookId) => {
    try {
      const response = await fetch(`/api/peers/${peerId}/books/${bookId}`, { method: 'POST' })
      if (response.ok) {
        alert('书籍下载成功！')
        setPeerBooks(prev => prev.filter(b => b.id !== bookId))
      }
    } catch (error) {
      console.error('Error downloading book:', error)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">P2P 网络</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">在线节点</h2>
          <PeerList 
            peers={peers} 
            onSelectPeer={handleSyncPeer}
            selectedPeer={selectedPeer}
          />
        </div>

        {selectedPeer && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">节点书单</h2>
            <div className="space-y-3">
              {peerBooks.map(book => (
                <div key={book.id} className="border rounded-lg p-4 flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">{book.title}</h3>
                    <p className="text-sm text-gray-600">{book.description}</p>
                    <span className="text-xs text-gray-500">{book.chapter_count} 章</span>
                  </div>
                  <button
                    onClick={() => handleDownloadBook(selectedPeer, book.id)}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                  >
                    下载
                  </button>
                </div>
              ))}
              
              {peerBooks.length === 0 && (
                <p className="text-gray-500 text-center">该节点暂无共享书籍</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Network
