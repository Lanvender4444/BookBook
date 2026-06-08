import { useEffect, useState } from 'react'
import { useI18n } from '../i18n'
import PeerList from '../components/PeerList'
import ConfirmModal from '../components/ConfirmModal'

function Network() {
  const { t } = useI18n()
  const [peers, setPeers] = useState([])
  const [selectedPeer, setSelectedPeer] = useState(null)
  const [peerBooks, setPeerBooks] = useState([])
  const [downloadModal, setDownloadModal] = useState({ open: false, peerId: null, bookId: null })

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

  const handleDownloadClick = (peerId, bookId) => {
    setDownloadModal({ open: true, peerId, bookId })
  }

  const confirmDownload = async () => {
    const { peerId, bookId } = downloadModal
    try {
      const response = await fetch(`/api/peers/${peerId}/books/${bookId}`, { method: 'POST' })
      if (response.ok) {
        alert(t('network.downloadSuccess'))
        setPeerBooks(prev => prev.filter(b => b.id !== bookId))
      }
    } catch (error) {
      console.error('Error downloading book:', error)
    }
    setDownloadModal({ open: false, peerId: null, bookId: null })
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">{t('network.title')}</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">{t('network.nodes')}</h2>
          <PeerList 
            peers={peers} 
            onSelectPeer={handleSyncPeer}
            selectedPeer={selectedPeer}
          />
        </div>

        {selectedPeer && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">{t('network.books')}</h2>
            <div className="space-y-3">
              {peerBooks.map(book => (
                <div key={book.id} className="border border-gray-200 rounded-lg p-4 flex justify-between items-center hover:shadow-md transition-shadow">
                  <div>
                    <h3 className="font-semibold">{book.title}</h3>
                    <p className="text-sm text-gray-600">{book.description}</p>
                    <span className="text-xs text-gray-500">{book.chapter_count} {t('history.chapters')}</span>
                  </div>
                  <button
                    onClick={() => handleDownloadClick(selectedPeer, book.id)}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    {t('network.download')}
                  </button>
                </div>
              ))}
              
              {peerBooks.length === 0 && (
                <p className="text-gray-500 text-center py-8">{t('network.noBooks')}</p>
              )}
            </div>
          </div>
        )}
      </div>

      <ConfirmModal
        isOpen={downloadModal.open}
        title={t('network.download')}
        message={t('network.confirmDownload')}
        confirmText={t('modal.confirm')}
        cancelText={t('modal.cancel')}
        onConfirm={confirmDownload}
        onCancel={() => setDownloadModal({ open: false, peerId: null, bookId: null })}
      />
    </div>
  )
}

export default Network
