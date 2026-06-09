import { useEffect, useState } from 'react'
import { useI18n } from '../i18n'
import ConfirmModal from '../components/ConfirmModal'

function Network() {
  const { t } = useI18n()
  const [activeTab, setActiveTab] = useState('share')
  const [shareTokens, setShareTokens] = useState([])
  const [shareForm, setShareForm] = useState({ book_id: '', expires_hours: 24 })
  const [books, setBooks] = useState([])
  const [connectForm, setConnectForm] = useState({ host: '', port: 47833 })
  const [peerBooks, setPeerBooks] = useState([])
  const [connecting, setConnecting] = useState(false)
  const [redeemForm, setRedeemForm] = useState({ token: '', host: '', local_host: '', port: 47833 })
  const [redeeming, setRedeeming] = useState(false)
  const [downloadModal, setDownloadModal] = useState({ open: false, peerHost: '', bookId: '' })
  const [message, setMessage] = useState('')
  const [copiedToken, setCopiedToken] = useState('')
  const [myInfo, setMyInfo] = useState({ user_id: '', host: '', port: 47833 })
  const [loadingShares, setLoadingShares] = useState(false)

  useEffect(() => {
    fetchBooks()
    fetchMyInfo()
    fetchShareTokens()
  }, [])

  const fetchMyInfo = async () => {
    try {
      const response = await fetch('/api/peers/me')
      if (response.ok) {
        const data = await response.json()
        setMyInfo(data)
      }
    } catch (error) {
      console.error('Error fetching my info:', error)
    }
  }

  const fetchBooks = async () => {
    try {
      const response = await fetch('/api/books')
      const data = await response.json()
      setBooks(data)
    } catch (error) {
      console.error('Error fetching books:', error)
    }
  }

  const fetchShareTokens = async () => {
    setLoadingShares(true)
    try {
      const response = await fetch('/api/peers/shares')
      if (response.ok) {
        const data = await response.json()
        setShareTokens(data.shares || [])
      }
    } catch (error) {
      console.error('Error fetching tokens:', error)
    } finally {
      setLoadingShares(false)
    }
  }

  const handleCreateShare = async () => {
    try {
      const response = await fetch('/api/peers/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: shareForm.book_id || null,
          expires_hours: shareForm.expires_hours
        })
      })
      const data = await response.json()
      if (response.ok) {
        setShareTokens(prev => [data, ...prev])
        setMessage(t('network.shareCreated'))
        setCopiedToken('')
      } else {
        setMessage(data.detail || 'Error')
      }
    } catch (error) {
      setMessage('Error: ' + error.message)
    }
  }

  const handleCopyShareUrl = (shareUrl) => {
    navigator.clipboard.writeText(shareUrl).then(() => {
      setCopiedToken(shareUrl)
      setTimeout(() => setCopiedToken(''), 2000)
    })
  }

  const handleConnect = async () => {
    let host = connectForm.host.trim()
    let port = connectForm.port
    // 如果用户输入了 host:port 格式，自动拆分
    if (host.includes(':')) {
      const parts = host.split(':')
      if (parts.length === 2 && !isNaN(parseInt(parts[1]))) {
        host = parts[0]
        port = parseInt(parts[1])
      }
    }
    if (!host) return
    setConnecting(true)
    setMessage('')
    try {
      const response = await fetch(`/api/peers/${host}/books?port=${port}`, {
        method: 'POST'
      })
      if (response.ok) {
        const data = await response.json()
        setPeerBooks(data.books || [])
        setMessage(t('network.connected'))
      } else {
        const error = await response.json()
        setMessage(error.detail || t('network.connectFailed'))
        setPeerBooks([])
      }
    } catch (error) {
      setMessage(t('network.connectFailed') + ': ' + error.message)
      setPeerBooks([])
    }
    setConnecting(false)
  }

  const handleDownloadClick = (peerHost, bookId) => {
    setDownloadModal({ open: true, peerHost, bookId })
  }

  const confirmDownload = async () => {
    let { peerHost, bookId } = downloadModal
    let port = connectForm.port
    // 自动拆分 host:port
    if (peerHost && peerHost.includes(':')) {
      const parts = peerHost.split(':')
      if (parts.length === 2 && !isNaN(parseInt(parts[1]))) {
        peerHost = parts[0]
        port = parseInt(parts[1])
      }
    }
    try {
      const response = await fetch(`/api/peers/${peerHost}/books/${bookId}/download?port=${port}`, {
        method: 'POST'
      })
      if (response.ok) {
        const data = await response.json()
        setMessage(t('network.downloadSuccess'))
        setPeerBooks(prev => prev.filter(b => b.id !== bookId))
        fetchBooks()
      } else {
        const error = await response.json()
        setMessage(error.detail || t('network.downloadFailed'))
      }
    } catch (error) {
      setMessage(t('network.downloadFailed') + ': ' + (error.message || ''))
    }
    setDownloadModal({ open: false, peerHost: '', bookId: '' })
    // 自动滚动到顶部，让用户看到提示消息
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // 解析分享链接，自动填充 host/port/token
  const parseShareLink = (link) => {
    try {
      if (link.startsWith('bookbook://')) {
        const url = new URL(link.replace('bookbook://', 'http://'))
        const token = url.searchParams.get('token')
        const host = url.searchParams.get('host')
        const public_host = url.searchParams.get('public_host')
        const port = url.searchParams.get('port')
        if (token) {
          setRedeemForm(prev => ({
            ...prev,
            token,
            host: public_host || host || prev.host,
            local_host: host || prev.host,
            port: port ? parseInt(port) : prev.port
          }))
          setMessage(t('network.autoFilled'))
          return true
        }
      }
      // 如果不是 bookbook:// 格式，尝试直接作为 token
      if (link.length > 10 && !link.includes(' ')) {
        setRedeemForm(prev => ({ ...prev, token: link }))
        return true
      }
    } catch (e) {
      // ignore parse errors
    }
    return false
  }

  const handleRedeem = async () => {
    let token = redeemForm.token.trim()
    let host = redeemForm.host.trim()
    let local_host = redeemForm.local_host.trim()
    let port = redeemForm.port

    // 自动尝试从 URL 中提取 token / host / port
    if (token.startsWith('bookbook://')) {
      try {
        const url = new URL(token.replace('bookbook://', 'http://'))
        const extractedToken = url.searchParams.get('token')
        if (extractedToken) {
          token = extractedToken
          const urlHost = url.searchParams.get('public_host') || url.searchParams.get('host')
          const urlPort = url.searchParams.get('port')
          if (urlHost && !host) host = urlHost
          if (urlHost && !local_host) local_host = url.searchParams.get('host') || urlHost
          if (urlPort) port = parseInt(urlPort)
        }
      } catch (e) {
        // 解析失败继续用原值
      }
    }

    if (!token || !host) return
    setRedeeming(true)
    setMessage('')
    try {
      const response = await fetch('/api/peers/redeem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token,
          host,
          local_host,
          port
        })
      })
      if (response.ok) {
        const data = await response.json()
        if (data.saved_ids && data.saved_ids.length > 1) {
          setMessage(t('network.booksDownloaded', { count: data.saved_ids.length }))
        } else {
          setMessage(t('network.downloadSuccess'))
        }
        fetchBooks()
      } else {
        const error = await response.json()
        setMessage(error.detail || t('network.redeemFailed'))
      }
    } catch (error) {
      setMessage(t('network.redeemFailed') + ': ' + error.message)
    }
    setRedeeming(false)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">{t('network.title')}</h1>

      {/* My Info Card */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-gray-500">{t('network.userId')}:</span>
            <span className="font-mono bg-gray-100 px-2 py-1 rounded">{myInfo.user_id}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-gray-500">{t('network.currentIp')}:</span>
            <span className="font-mono bg-gray-100 px-2 py-1 rounded text-indigo-600">{myInfo.host}:{myInfo.port}</span>
            <button
              onClick={() => {
                navigator.clipboard.writeText(`${myInfo.host}:${myInfo.port}`)
                setCopiedToken('ip')
                setTimeout(() => setCopiedToken(''), 2000)
              }}
              className="text-xs px-2 py-1 bg-indigo-50 text-indigo-600 rounded hover:bg-indigo-100"
            >
              {copiedToken === 'ip' ? '✓' : t('network.copy')}
            </button>
          </div>
          {myInfo.public_ip && (
            <div className="flex items-center gap-2">
              <span className="text-gray-500">公网 IP:</span>
              <span className="font-mono bg-green-100 px-2 py-1 rounded text-green-700">{myInfo.public_ip}:{myInfo.port}</span>
              <span className="text-xs text-green-600 bg-green-50 px-1.5 py-0.5 rounded">NAT 可穿透</span>
            </div>
          )}
          {!myInfo.public_ip && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded">
                当前处于局域网内，公网访问需要对方在同一网络或配置端口转发
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Tab navigation */}
      <div className="flex space-x-2 mb-6">
        {[
          { key: 'share', label: t('network.shareTab'), icon: '🔗' },
          { key: 'connect', label: t('network.connectTab'), icon: '🌐' },
          { key: 'redeem', label: t('network.redeemTab'), icon: '📥' }
        ].map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              activeTab === key
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            {icon} {label}
          </button>
        ))}
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded-lg text-sm ${
          message.includes(t('network.downloadSuccess')) ||
          message.includes(t('network.connected')) ||
          message.includes(t('network.shareCreated')) ||
          message.includes(t('network.autoFilled')) ||
          message.includes(t('network.booksDownloaded'))
            ? 'bg-green-50 text-green-700 border border-green-200'
            : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message}
        </div>
      )}

      {/* Share Tab */}
      {activeTab === 'share' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">{t('network.createShare')}</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('network.selectBook')}</label>
                <select
                  value={shareForm.book_id}
                  onChange={(e) => setShareForm({...shareForm, book_id: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="">{t('network.allBooks')}</option>
                  {books.map(book => (
                    <option key={book.id} value={book.id}>{book.title}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('network.expireTime')}</label>
                <select
                  value={shareForm.expires_hours}
                  onChange={(e) => setShareForm({...shareForm, expires_hours: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value={1}>1 {t('network.hour')}</option>
                  <option value={6}>6 {t('network.hours')}</option>
                  <option value={24}>24 {t('network.hours')}</option>
                  <option value={72}>3 {t('network.days')}</option>
                  <option value={168}>7 {t('network.days')}</option>
                </select>
              </div>

              <button
                onClick={handleCreateShare}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                {t('network.generateLink')}
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">{t('network.myShareLinks')}</h2>
            {loadingShares ? (
              <p className="text-gray-500 text-center py-8">{t('network.downloading')}</p>
            ) : shareTokens.length === 0 ? (
              <p className="text-gray-500 text-center py-8">{t('network.noShareLinks')}</p>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {shareTokens.map((token, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-500">
                        {token.book_id
                          ? books.find(b => b.id === token.book_id)?.title || token.book_id
                          : t('network.allBooks')
                        }
                      </span>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleCopyShareUrl(token.share_url)}
                          className="px-3 py-1 text-sm bg-indigo-50 text-indigo-600 rounded-md hover:bg-indigo-100"
                        >
                          {copiedToken === token.share_url ? '✓' : t('network.copy')}
                        </button>
                      </div>
                    </div>
                    <div className="bg-gray-50 rounded p-2 text-xs font-mono break-all text-gray-600 mb-1">
                      {token.share_url}
                    </div>
                    {token.host && (
                      <div className="text-xs text-gray-400 mb-1">
                        {t('network.currentIp')}: {token.host}:{token.port}
                        {token.public_host && ` (公网: ${token.public_host}:${token.port})`}
                      </div>
                    )}
                    {token.expires_at && (
                      <p className="text-xs text-gray-400">
                        {t('network.expiresAt')}: {new Date(token.expires_at).toLocaleString()}
                      </p>
                    )}
                    {token.used_count > 0 && (
                      <p className="text-xs text-gray-400 mt-1">
                        {t('network.download')}: {token.used_count} {t('network.times')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Connect Tab */}
      {activeTab === 'connect' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">{t('network.connectPeer')}</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('network.peerAddress')}
                </label>
                <input
                  type="text"
                  value={connectForm.host}
                  onChange={(e) => setConnectForm({...connectForm, host: e.target.value})}
                  placeholder="192.168.1.100 or example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('network.peerPort')}
                </label>
                <input
                  type="number"
                  value={connectForm.port}
                  onChange={(e) => setConnectForm({...connectForm, port: parseInt(e.target.value) || 47833})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>

              <button
                onClick={handleConnect}
                disabled={connecting || !connectForm.host}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {connecting ? t('network.connecting') : t('network.connect')}
              </button>
            </div>

            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-700 mb-2">{t('network.shareHelpTitle')}</h3>
              <p className="text-sm text-gray-600 mb-2">
                {t('network.shareHelpDesc')}
              </p>
              <div className="bg-white rounded p-3 text-xs font-mono text-gray-500 border border-gray-200">
                bookbook://share?token=xxx&peer=xxx&host=xxx&port=xxx&v=1
              </div>
            </div>
          </div>

          {peerBooks.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">
                {t('network.peerBooks')} ({connectForm.host})
              </h2>
              <div className="space-y-3">
                {peerBooks.map(book => (
                  <div key={book.id} className="border border-gray-200 rounded-lg p-4 flex justify-between items-center hover:shadow-md transition-shadow">
                    <div className="flex-1 min-w-0 mr-4">
                      <h3 className="font-semibold truncate">{book.title}</h3>
                      <p className="text-sm text-gray-600 truncate">{book.description}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-500">{book.chapter_count} {t('history.chapters')}</span>
                        <span className={`text-xs px-1.5 py-0.5 rounded ${
                          book.source === 'local' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                        }`}>
                          {book.source === 'local' ? t('network.local') : 'P2P'}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDownloadClick(connectForm.host, book.id)}
                      className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex-shrink-0"
                    >
                      {t('network.download')}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Redeem Tab */}
      {activeTab === 'redeem' && (
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">{t('network.redeemShare')}</h2>
            <p className="text-sm text-gray-600 mb-4">
              {t('network.redeemHelpDesc')}
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('network.shareUrl')}
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={redeemForm.token}
                    onChange={(e) => setRedeemForm({...redeemForm, token: e.target.value})}
                    placeholder="bookbook://share?token=xxx&peer=xxx&host=xxx&port=xxx&v=1"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono"
                  />
                  <button
                    onClick={() => parseShareLink(redeemForm.token)}
                    className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm whitespace-nowrap"
                  >
                    {t('network.parseLink')}
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  {t('network.shareToken')} / {t('network.shareUrl')}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('network.peerHost')}
                </label>
                <input
                  type="text"
                  value={redeemForm.host}
                  onChange={(e) => setRedeemForm({...redeemForm, host: e.target.value})}
                  placeholder="192.168.1.100 or example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('network.peerPort')}
                </label>
                <input
                  type="number"
                  value={redeemForm.port}
                  onChange={(e) => setRedeemForm({...redeemForm, port: parseInt(e.target.value) || 47833})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>

              <button
                onClick={handleRedeem}
                disabled={redeeming || !redeemForm.token || !redeemForm.host}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {redeeming ? t('network.downloading') : t('network.redeemBtn')}
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={downloadModal.open}
        title={t('network.download')}
        message={t('network.confirmDownload')}
        confirmText={t('modal.confirm')}
        cancelText={t('modal.cancel')}
        onConfirm={confirmDownload}
        onCancel={() => setDownloadModal({ open: false, peerHost: '', bookId: '' })}
      />
    </div>
  )
}

export default Network
