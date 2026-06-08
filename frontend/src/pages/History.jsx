import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

function History() {
  const [histories, setHistories] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchHistories()
  }, [filter])

  const fetchHistories = async () => {
    setLoading(true)
    try {
      const url = filter === 'all' 
        ? '/api/generate/history'
        : `/api/generate/history?status=${filter}`
      const response = await fetch(url)
      const data = await response.json()
      setHistories(data)
    } catch (error) {
      console.error('Error fetching histories:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (historyId) => {
    if (confirm('确定要删除这条记录吗？')) {
      try {
        await fetch(`/api/generate/history/${historyId}`, { method: 'DELETE' })
        fetchHistories()
      } catch (error) {
        console.error('Error deleting history:', error)
      }
    }
  }

  const handleViewBook = (bookId) => {
    if (bookId) {
      navigate(`/reader/${bookId}`)
    }
  }

  const handleContinueGenerate = (history) => {
    // 跳转到生成页并填充之前的参数
    const params = new URLSearchParams({
      prompt: history.prompt,
      difficulty: history.requirements?.difficulty || '中等',
      word_count: history.requirements?.word_count || '5000',
      chapter_count: history.requirements?.chapter_count || '5-8',
      style: history.requirements?.style || '科普向'
    })
    navigate(`/generate?${params.toString()}`)
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: { text: '生成中', color: 'bg-yellow-100 text-yellow-700', icon: '⏳' },
      completed: { text: '已完成', color: 'bg-green-100 text-green-700', icon: '✅' },
      failed: { text: '失败', color: 'bg-red-100 text-red-700', icon: '❌' },
      deleted: { text: '已删除', color: 'bg-gray-100 text-gray-500', icon: '🗑️' }
    }
    return badges[status] || badges.pending
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">生成历史</h1>
        <button
          onClick={() => navigate('/generate')}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          新建生成
        </button>
      </div>

      {/* 筛选按钮 */}
      <div className="flex space-x-2 mb-6">
        {[
          { key: 'all', label: '全部' },
          { key: 'pending', label: '进行中' },
          { key: 'completed', label: '已完成' },
          { key: 'failed', label: '失败' },
          { key: 'deleted', label: '已删除' }
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              filter === key 
                ? 'bg-indigo-600 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* 列表 */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : histories.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📝</div>
          <p className="text-gray-500">暂无历史记录</p>
          <button
            onClick={() => navigate('/generate')}
            className="mt-4 text-indigo-600 hover:text-indigo-700"
          >
            去生成一本电子书
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {histories.map((history) => {
            const statusInfo = getStatusBadge(history.status)
            return (
              <div 
                key={history.id} 
                className="bg-white rounded-lg shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}>
                        {statusInfo.icon} {statusInfo.text}
                      </span>
                      <span className="text-xs text-gray-400">
                        #{history.id}
                      </span>
                    </div>
                    
                    <p className="text-gray-800 font-medium mb-2 line-clamp-2">
                      {history.prompt}
                    </p>
                    
                    {history.outline?.title && (
                      <p className="text-sm text-gray-600 mb-2">
                        📖 {history.outline.title}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>创建: {formatDate(history.created_at)}</span>
                      {history.completed_at && (
                        <span>完成: {formatDate(history.completed_at)}</span>
                      )}
                      {history.requirements && (
                        <span className="hidden sm:inline">
                          {history.requirements.difficulty} · {history.requirements.word_count}字
                        </span>
                      )}
                    </div>
                    
                    {history.error_message && (
                      <p className="mt-2 text-sm text-red-500 bg-red-50 p-2 rounded">
                        {history.error_message}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {history.status === 'pending' && (
                      <button
                        onClick={() => handleDelete(history.id)}
                        className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md"
                      >
                        取消
                      </button>
                    )}
                    {history.status === 'completed' && history.book_id && (
                      <button
                        onClick={() => handleViewBook(history.book_id)}
                        className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                      >
                        阅读
                      </button>
                    )}
                    {(history.status === 'failed' || history.status === 'deleted') && (
                      <button
                        onClick={() => handleContinueGenerate(history)}
                        className="px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 rounded-md"
                      >
                        重新生成
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(history.id)}
                      className="p-1.5 text-gray-400 hover:text-red-500 rounded-md"
                      title="删除"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default History
