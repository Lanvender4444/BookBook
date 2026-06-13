import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useI18n } from '../i18n'
import ConfirmModal from '../components/ConfirmModal'
import TypewriterHeading from '../components/TypewriterHeading'

const titleSpeed = (locale) => (['zh-CN', 'zh-TW', 'ja', 'ko'].includes(locale) ? 200 : 120)

function History() {
  const { t, locale } = useI18n()
  const [histories, setHistories] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState(null)
  const [taskProgress, setTaskProgress] = useState({})
  const [deleteModal, setDeleteModal] = useState({ open: false, historyId: null, mode: 'soft' })
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchHistories()
  }, [filter])

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
        setTaskProgress(prev => ({ ...prev, [historyId]: data.task_status }))
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

  const handleDeleteClick = (e, historyId, mode = 'soft') => {
    e.stopPropagation()
    setDeleteModal({ open: true, historyId, mode })
  }

  const confirmDelete = async () => {
    const id = deleteModal.historyId
    if (!id) return
    try {
      if (deleteModal.mode === 'permanent') {
        await fetch(`/api/generate/history/${id}/permanent`, { method: 'DELETE' })
      } else {
        await fetch(`/api/generate/history/${id}/cancel`, { method: 'POST' })
      }
      fetchHistories()
    } catch (error) {
      console.error('Error deleting history:', error)
    }
    setDeleteModal({ open: false, historyId: null, mode: 'soft' })
  }

  const handleClearDeleted = async () => {
    try {
      await fetch('/api/generate/history/clear-deleted', { method: 'DELETE' })
      fetchHistories()
    } catch (error) {
      console.error('Error clearing deleted:', error)
    }
  }

  const handleViewBook = (e, bookId) => {
    e.stopPropagation()
    if (bookId) navigate(`/reader/${bookId}`)
  }

  const handleContinueGenerate = (e, history) => {
    e.stopPropagation()
    const params = new URLSearchParams({
      prompt: history.prompt,
      difficulty: history.requirements?.difficulty || 'medium',
      word_count: history.requirements?.word_count || '5000',
      chapter_count: history.requirements?.chapter_count || '5-8',
      style: history.requirements?.style || '科普向'
    })
    navigate(`/generate?${params.toString()}`)
  }

  const handleViewProgress = (e, history) => {
    e.stopPropagation()
    navigate(`/generate?history_id=${history.id}`)
  }

  const toggleExpand = (historyId) => {
    setExpandedId(expandedId === historyId ? null : historyId)
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: { text: t('history.pending'), color: 'bg-yellow-100 text-yellow-700', icon: '⏳' },
      completed: { text: t('history.completed'), color: 'bg-green-100 text-green-700', icon: '✅' },
      failed: { text: t('history.failed'), color: 'bg-red-100 text-red-700', icon: '❌' },
      deleted: { text: t('history.deleted'), color: 'bg-gray-100 text-gray-500', icon: '' }
    }
    return badges[status] || badges.pending
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString()
  }

  const filterOptions = [
    { key: 'all', label: t('history.all') },
    { key: 'pending', label: t('history.pending') },
    { key: 'completed', label: t('history.completed') },
    { key: 'failed', label: t('history.failed') },
    { key: 'deleted', label: t('history.deleted') }
  ]

  // 根据搜索关键词过滤
  const filteredHistories = histories.filter(history => {
    if (!searchQuery.trim()) return true
    const query = searchQuery.toLowerCase()
    return (
      history.prompt?.toLowerCase().includes(query) ||
      history.outline?.title?.toLowerCase().includes(query) ||
      history.status?.toLowerCase().includes(query)
    )
  })

  const hasDeleted = histories.some(h => h.status === 'deleted')

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <TypewriterHeading text={t('history.title')} speed={titleSpeed(locale)} fontSize="1.875rem" className="text-gray-900" />
        <button
          onClick={() => navigate('/generate')}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          {t('history.newGenerate')}
        </button>
      </div>

      {/* 搜索框 */}
      <div className="mb-4">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('history.searchPlaceholder') || '搜索历史记录...'}
            className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
          />
          <svg className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-2 text-gray-400 hover:text-gray-600"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex space-x-2">
          {filterOptions.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                filter === key
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* 清空已删除按钮 */}
        {hasDeleted && (
          <button
            onClick={() => {
              if (window.confirm(t('history.confirmClearDeleted') || '确定要清空所有已删除的记录吗？')) {
                handleClearDeleted()
              }
            }}
            className="text-sm text-red-600 hover:text-red-700 hover:bg-red-50 px-3 py-2 rounded-lg transition-colors"
          >
            {t('history.clearDeleted') || '清空已删除'}
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : filteredHistories.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📝</div>
          <p className="text-gray-500">
            {searchQuery ? t('history.noSearchResults') || '没有找到匹配的记录' : t('history.noRecords')}
          </p>
          {!searchQuery && (
            <button
              onClick={() => navigate('/generate')}
              className="mt-4 text-indigo-600 hover:text-indigo-700"
            >
              {t('history.goGenerate')}
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredHistories.map((history) => {
            const statusInfo = getStatusBadge(history.status)
            const isExpanded = expandedId === history.id

            return (
              <div
                key={history.id}
                className={`bg-white rounded-lg border transition-all ${
                  isExpanded ? 'shadow-md border-indigo-200' : 'shadow-sm border-gray-100 hover:shadow-md hover:border-gray-200'
                }`}
              >
                <div
                  className="p-4 flex items-center gap-4 cursor-pointer select-none"
                  onClick={() => toggleExpand(history.id)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}>
                        {statusInfo.icon && <span className="mr-1">{statusInfo.icon}</span>}
                        {statusInfo.text}
                      </span>
                      <span className="text-xs text-gray-400">#{history.id}</span>
                    </div>
                    <p className="text-gray-800 font-medium truncate">{history.prompt}</p>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {history.status === 'pending' && (
                      <>
                        <button type="button" onClick={(e) => handleViewProgress(e, history)}
                          className="px-3 py-1.5 text-sm bg-indigo-600 text-white hover:bg-indigo-700 rounded-lg">
                          {t('history.viewProgress')}
                        </button>
                        <button type="button" onClick={(e) => handleDeleteClick(e, history.id, 'soft')}
                          className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg">
                          {t('history.cancel')}
                        </button>
                      </>
                    )}
                    {history.status === 'completed' && history.book_id && (
                      <button type="button" onClick={(e) => handleViewBook(e, history.book_id)}
                        className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                        {t('history.read')}
                      </button>
                    )}
                    {(history.status === 'failed' || history.status === 'deleted') && (
                      <button type="button" onClick={(e) => handleContinueGenerate(e, history)}
                        className="px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg">
                        {t('history.regenerate')}
                      </button>
                    )}
                    {/* 删除按钮：已删除记录用永久删除，其他用取消 */}
                    {history.status === 'deleted' ? (
                      <button type="button" onClick={(e) => handleDeleteClick(e, history.id, 'permanent')}
                        className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg">
                        {t('history.delete')}
                      </button>
                    ) : (
                      <button type="button" onClick={(e) => handleDeleteClick(e, history.id, 'soft')}
                        className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg" title={t('history.delete')}>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    )}
                  </div>

                  <svg className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>

                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-100 pt-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                      <div>
                        <span className="text-gray-500">{t('history.createdAt')}</span>
                        <p className="text-gray-800">{formatDate(history.created_at)}</p>
                      </div>
                      {history.completed_at && (
                        <div>
                          <span className="text-gray-500">{t('history.completedAt')}</span>
                          <p className="text-gray-800">{formatDate(history.completed_at)}</p>
                        </div>
                      )}
                      {history.requirements && (
                        <>
                          <div>
                            <span className="text-gray-500">{t('history.difficulty')}</span>
                            <p className="text-gray-800">{history.requirements.difficulty || '-'}</p>
                          </div>
                          <div>
                            <span className="text-gray-500">{t('history.wordCount')}</span>
                            <p className="text-gray-800">{history.requirements.word_count || '-'}字</p>
                          </div>
                        </>
                      )}
                      {history.language && (
                        <div>
                          <span className="text-gray-500">{t('generate.language')}</span>
                          <p className="text-gray-800">{history.language}</p>
                        </div>
                      )}
                    </div>

                    {history.outline && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-700 mb-2">
                          {t('history.outline')}：{history.outline.title}
                        </h4>
                        {history.outline.description && (
                          <p className="text-sm text-gray-600 mb-3">{history.outline.description}</p>
                        )}
                        {history.outline.chapters && history.outline.chapters.length > 0 && (
                          <div className="space-y-1">
                            <p className="text-xs text-gray-500 mb-2">
                              {history.outline.chapters.length} {t('history.chapters')}
                            </p>
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

                    {history.error_message && (
                      <div className="mt-3 p-3 bg-red-50 rounded-lg">
                        <p className="text-sm text-red-600">{t('history.error')}: {history.error_message}</p>
                      </div>
                    )}

                    {history.status === 'pending' && taskProgress[history.id] && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                          <p className="text-sm font-medium text-blue-700">{t('history.realtimeProgress')}</p>
                        </div>
                        <p className="text-sm text-blue-600">
                          {taskProgress[history.id].progress?.message || t('history.processing')}
                        </p>
                        {taskProgress[history.id].progress?.current_chapter > 0 && (
                          <div className="mt-2">
                            <div className="flex justify-between text-xs text-blue-500 mb-1">
                              <span>{t('history.chapter').replace('{current}', taskProgress[history.id].progress.current_chapter)}</span>
                              <span>{t('history.totalChapters').replace('{total}', taskProgress[history.id].progress.total_chapters)}</span>
                            </div>
                            <div className="w-full bg-blue-200 rounded-full h-2">
                              <div
                                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${(taskProgress[history.id].progress.current_chapter / taskProgress[history.id].progress.total_chapters) * 100}%` }}
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

      <ConfirmModal
        isOpen={deleteModal.open}
        title={deleteModal.mode === 'permanent' ? (t('history.confirmPermanentDeleteTitle') || '永久删除') : t('history.confirmDeleteTitle')}
        message={deleteModal.mode === 'permanent' ? (t('history.confirmPermanentDelete') || '确定要永久删除这条记录吗？此操作不可撤销。') : t('history.confirmDelete')}
        confirmText={t('modal.confirm')}
        cancelText={t('modal.cancel')}
        danger={true}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteModal({ open: false, historyId: null, mode: 'soft' })}
      />
    </div>
  )
}

export default History
