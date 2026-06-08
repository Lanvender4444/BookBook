import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

function History() {
  const [histories, setHistories] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState(null)
  const [taskProgress, setTaskProgress] = useState({})
  const navigate = useNavigate()

  useEffect(() => {
    fetchHistories()
  }, [filter])

  // 定期刷新进行中任务的状态
  useEffect(() => {
    const interval = setInterval(() => {
      const pendingHistories = histories.filter(h => h.status === 'pending')
      if (pendingHistories.length > 0) {
        pendingHistories.forEach(h => fetchTaskProgress(h.id))
      }
    }, 2000)
    return () => clearInterval(interval)
  }, [histories])

  const fetchTaskProgress = async (historyId) => {
    try {
      const response = await fetch(`/api/generate/history/${historyId}`)
      const data = await response.json()
      if (data.task_status) {
        setTaskProgress(prev => ({
          ...prev,
          [historyId]: data.task_status
        }))
        
        // 如果任务完成，刷新列表
        if (data.task_status.status === 'completed' || data.task_status.status === 'failed') {
          fetchHistories()
        }
      }
    } catch (error) {
      console.error('Error fetching task progress:', error)
    }
  }

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

  const handleDelete = async (e, historyId) => {
    e.stopPropagation()
    if (confirm('确定要删除这条记录吗？')) {
      try {
        await fetch(`/api/generate/history/${historyId}`, { method: 'DELETE' })
        fetchHistories()
      } catch (error) {
        console.error('Error deleting history:', error)
      }
    }
  }

  const handleViewBook = (e, bookId) => {
    e.stopPropagation()
    if (bookId) {
      navigate(`/reader/${bookId}`)
    }
  }

  const handleContinueGenerate = (e, history) => {
    e.stopPropagation()
    const params = new URLSearchParams({
      prompt: history.prompt,
      difficulty: history.requirements?.difficulty || '中等',
      word_count: history.requirements?.word_count || '5000',
      chapter_count: history.requirements?.chapter_count || '5-8',
      style: history.requirements?.style || '科普向'
    })
    navigate(`/generate?${params.toString()}`)
  }

  const handleViewProgress = (e, history) => {
    e.stopPropagation()
    // 跳转到生成页面并重新连接到后台任务
    navigate(`/generate?history_id=${history.id}`)
  }

  const toggleExpand = (historyId) => {
    setExpandedId(expandedId === historyId ? null : historyId)
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
        <div className="space-y-3">
          {histories.map((history) => {
            const statusInfo = getStatusBadge(history.status)
            const isExpanded = expandedId === history.id
            
            return (
              <div 
                key={history.id} 
                className={`bg-white rounded-lg border transition-all cursor-pointer ${
                  isExpanded 
                    ? 'shadow-md border-indigo-200' 
                    : 'shadow-sm border-gray-100 hover:shadow-md hover:border-gray-200'
                }`}
                onClick={() => toggleExpand(history.id)}
              >
                {/* 主体行 */}
                <div className="p-4 flex items-center gap-4">
                  {/* 状态和标题 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}>
                        {statusInfo.icon} {statusInfo.text}
                      </span>
                      <span className="text-xs text-gray-400">#{history.id}</span>
                    </div>
                    <p className="text-gray-800 font-medium truncate">{history.prompt}</p>
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex items-center gap-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                    {history.status === 'pending' && (
                      <>
                        <button
                          onClick={(e) => handleViewProgress(e, history)}
                          className="px-3 py-1.5 text-sm bg-indigo-600 text-white hover:bg-indigo-700 rounded-md"
                        >
                          查看进度
                        </button>
                        <button
                          onClick={(e) => handleDelete(e, history.id)}
                          className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md"
                        >
                          取消
                        </button>
                      </>
                    )}
                    {history.status === 'completed' && history.book_id && (
                      <button
                        onClick={(e) => handleViewBook(e, history.book_id)}
                        className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                      >
                        阅读
                      </button>
                    )}
                    {(history.status === 'failed' || history.status === 'deleted') && (
                      <button
                        onClick={(e) => handleContinueGenerate(e, history)}
                        className="px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 rounded-md"
                      >
                        重新生成
                      </button>
                    )}
                    <button
                      onClick={(e) => handleDelete(e, history.id)}
                      className="p-1.5 text-gray-400 hover:text-red-500 rounded-md"
                      title="删除"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>

                  {/* 展开箭头 */}
                  <svg 
                    className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>

                {/* 展开内容 */}
                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-100 pt-4" onClick={(e) => e.stopPropagation()}>
                    {/* 基本信息 */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                      <div>
                        <span className="text-gray-500">创建时间</span>
                        <p className="text-gray-800">{formatDate(history.created_at)}</p>
                      </div>
                      {history.completed_at && (
                        <div>
                          <span className="text-gray-500">完成时间</span>
                          <p className="text-gray-800">{formatDate(history.completed_at)}</p>
                        </div>
                      )}
                      {history.requirements && (
                        <>
                          <div>
                            <span className="text-gray-500">难度</span>
                            <p className="text-gray-800">{history.requirements.difficulty || '-'}</p>
                          </div>
                          <div>
                            <span className="text-gray-500">目标字数</span>
                            <p className="text-gray-800">{history.requirements.word_count || '-'}字</p>
                          </div>
                        </>
                      )}
                    </div>

                    {/* 大纲预览 */}
                    {history.outline && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-700 mb-2">
                          📋 大纲：{history.outline.title}
                        </h4>
                        {history.outline.description && (
                          <p className="text-sm text-gray-600 mb-3">{history.outline.description}</p>
                        )}
                        {history.outline.chapters && history.outline.chapters.length > 0 && (
                          <div className="space-y-1">
                            <p className="text-xs text-gray-500 mb-2">章节列表 ({history.outline.chapters.length}章)</p>
                            {history.outline.chapters.map((chapter, idx) => (
                              <div key={idx} className="flex items-start gap-2 text-sm">
                                <span className="text-indigo-500 font-medium">{idx + 1}.</span>
                                <div>
                                  <span className="text-gray-800">{chapter.title}</span>
                                  {chapter.summary && (
                                    <span className="text-gray-500 ml-2">- {chapter.summary}</span>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* 错误信息 */}
                    {history.error_message && (
                      <div className="mt-3 p-3 bg-red-50 rounded-lg">
                        <p className="text-sm text-red-600">❌ {history.error_message}</p>
                      </div>
                    )}

                    {/* 实时进度（仅对进行中的任务） */}
                    {history.status === 'pending' && taskProgress[history.id] && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                          <p className="text-sm font-medium text-blue-700">实时进度</p>
                        </div>
                        <p className="text-sm text-blue-600">
                          {taskProgress[history.id].progress?.message || '处理中...'}
                        </p>
                        {taskProgress[history.id].progress?.current_chapter && (
                          <div className="mt-2">
                            <div className="flex justify-between text-xs text-blue-500 mb-1">
                              <span>第 {taskProgress[history.id].progress.current_chapter} 章</span>
                              <span>共 {taskProgress[history.id].progress.total_chapters} 章</span>
                            </div>
                            <div className="w-full bg-blue-200 rounded-full h-2">
                              <div 
                                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                style={{ 
                                  width: `${(taskProgress[history.id].progress.current_chapter / taskProgress[history.id].progress.total_chapters) * 100}%` 
                                }}
                              ></div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default History
