import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useI18n } from '../i18n'
import { api } from '../api'
import useStore from '../store'
import OutlineTree from '../components/OutlineTree'
import ProgressBar from '../components/ProgressBar'
import CustomSelect from '../components/CustomSelect'
import CustomInput from '../components/CustomInput'
import TypewriterHeading from '../components/TypewriterHeading'
import TypewriterPlaceholder from '../components/TypewriterPlaceholder'
import ProviderModal from '../components/ProviderModal'
import { sendSystemNotification, requestNotificationPermission } from '../utils/notify'

// 标签解析：以 # 为标记（如 "#小说 #悬疑"）；无 # 时兼容逗号分隔
export function parseTags(input) {
  if (!input) return []
  const clean = (s) => s.trim().replace(/[,，、;；\s]+$/g, '').trim()
  if (input.includes('#')) {
    return input.split('#').map(clean).filter(Boolean)
  }
  return input.split(/[,，、;；]/).map(clean).filter(Boolean)
}

function Generate() {
  const { t, locale } = useI18n()
  const [searchParams] = useSearchParams()
  const [prompt, setPrompt] = useState(searchParams.get('prompt') || '')
  const [requirements, setRequirements] = useState({
    difficulty: searchParams.get('difficulty') || 'medium',
    word_count: searchParams.get('word_count') || '5000',
    chapter_count: searchParams.get('chapter_count') || '5-8'
  })
  const [tagsInput, setTagsInput] = useState('')
  const [outline, setOutline] = useState(null)
  const [chapters, setChapters] = useState([])
  const [generating, setGenerating] = useState(false)
  const [currentChapter, setCurrentChapter] = useState(0)
  const [totalChapters, setTotalChapters] = useState(0)
  const [historyId, setHistoryId] = useState(null)
  const [statusMessage, setStatusMessage] = useState('')
  const [showProviderModal, setShowProviderModal] = useState(false)
  const [cards, setCards] = useState([])
  const [cardId, setCardId] = useState('')
  const [extraRequirements, setExtraRequirements] = useState('')
  const [showCardPicker, setShowCardPicker] = useState(false)
  const selectedCard = cards.find((c) => c.id === cardId) || null
  const activeModel = useStore((s) => s.activeModel)
  const navigate = useNavigate()
  
  const abortControllerRef = useRef(null)
  const isMountedRef = useRef(true)
  const generatingRef = useRef(false)

  useEffect(() => {
    return () => {
      isMountedRef.current = false
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  useEffect(() => {
    api.listCards().then((c) => setCards(Array.isArray(c) ? c : [])).catch(() => {})
  }, [])

  useEffect(() => {
    const savedHistoryId = searchParams.get('history_id')
    if (savedHistoryId) {
      reconnectToTask(parseInt(savedHistoryId))
    }
  }, [searchParams])

  const reconnectToTask = async (taskId) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    
    abortControllerRef.current = new AbortController()
    const signal = abortControllerRef.current.signal
    
    setGenerating(true)
    generatingRef.current = true
    setHistoryId(taskId)
    setStatusMessage(t('generate.reconnecting'))
    
    try {
      const response = await fetch(`/api/generate/stream/${taskId}`, { signal })
      await processSSEStream(response, signal)
    } catch (error) {
      if (error.name !== 'AbortError') {
        setStatusMessage(t('generate.reconnectFailed'))
      }
      if (isMountedRef.current) {
        setGenerating(false)
        generatingRef.current = false
      }
    }
  }

  const processSSEStream = async (response, signal) => {
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      if (signal.aborted) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6).trim()
            const data = JSON.parse(jsonStr)
            
            if (data.history_id) {
              setHistoryId(data.history_id)
            } else if (data.type === 'progress') {
              handleProgressEvent(data.data)
            } else if (data.type === 'done') {
              handleDoneEvent(data.data)
            } else if (data.type === 'error') {
              handleErrorEvent(data.data)
            }
          } catch (e) {}
        }
      }
    }
  }

  const handleProgressEvent = (data) => {
    setStatusMessage(data.message || '')
    
    if (data.stage === 'outline' || data.stage === 'outline_done') {
      if (data.outline) {
        setOutline(data.outline)
        setTotalChapters(data.outline.chapters?.length || 0)
      }
    } else if (data.stage === 'chapter' || data.stage === 'chapter_done') {
      setCurrentChapter(data.current_chapter || 0)
      setTotalChapters(data.total_chapters || 0)
      
      if (data.chapter_content) {
        setChapters(prev => {
          if (prev.some(c => c.index === data.current_chapter - 1)) return prev
          return [...prev, {
            index: data.current_chapter - 1,
            title: data.chapter_title,
            content: data.chapter_content
          }]
        })
      }
    }
  }

  const handleDoneEvent = (data) => {
    setGenerating(false)
    generatingRef.current = false
    setStatusMessage(t('generate.completed'))
    if (data.book_id) {
      const title = data.book_title || outline?.title || '未命名电子书'
      // 发送系统级右下角通知，无论当前在浏览什么页面都会显示
      sendSystemNotification(
        '电子书制作完成',
        `《${title}》已生成完毕，点击查看`,
        () => {
          window.focus()
          navigate(`/reader/${data.book_id}`)
        }
      )
    }
  }

  const handleErrorEvent = (data) => {
    setGenerating(false)
    generatingRef.current = false
    setStatusMessage(`${t('generate.error')}: ${data.message}`)
  }

  const handleGenerate = async () => {
    if (!prompt.trim() || generatingRef.current) return

    // 预请求通知权限，确保完成后能弹出系统通知
    requestNotificationPermission()

    if (abortControllerRef.current) abortControllerRef.current.abort()

    abortControllerRef.current = new AbortController()
    const signal = abortControllerRef.current.signal

    setGenerating(true)
    generatingRef.current = true
    setOutline(null)
    setChapters([])
    setCurrentChapter(0)
    setTotalChapters(0)
    setHistoryId(null)
    setStatusMessage(t('generate.preparing'))

    try {
      const response = await fetch('/api/generate/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          requirements: { ...requirements, language: locale },
          provider_id: activeModel?.provider_id || null,
          model_name: activeModel?.model_name || null,
          card_id: cardId || null,
          extra_requirements: extraRequirements,
          tags: parseTags(tagsInput),
        }),
        signal
      })
      await processSSEStream(response, signal)
    } catch (error) {
      if (error.name !== 'AbortError' && isMountedRef.current) {
        setGenerating(false)
        generatingRef.current = false
      }
    }
  }

  const handleCancel = async () => {
    if (abortControllerRef.current) abortControllerRef.current.abort()
    if (historyId) {
      try { await fetch(`/api/generate/${historyId}/cancel`, { method: 'POST' }) } catch (e) {}
    }
    setGenerating(false)
    generatingRef.current = false
    setStatusMessage(t('generate.cancelled'))
  }

  const difficultyOptions = [
    { value: 'simple', label: t('generate.simple') },
    { value: 'medium', label: t('generate.medium') },
    { value: 'hard', label: t('generate.hard') }
  ]

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <TypewriterHeading text={t('generate.title')} speed={['zh-CN', 'zh-TW', 'ja', 'ko'].includes(locale) ? 200 : 120} className="text-gray-900 mb-8" />
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('generate.description')}
        </label>
        <div className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500 hover:border-gray-400 transition-all bg-transparent relative z-10"
            disabled={generating}
          />
          {!prompt && !generating && (
            <div className="absolute top-2 left-3 z-0 pointer-events-none text-gray-400 text-sm">
              <TypewriterPlaceholder
                text={t('generate.placeholder')}
                speed={['zh-CN', 'zh-TW', 'ja', 'ko'].includes(locale) ? 160 : 80}
              />
            </div>
          )}
        </div>
        
        {activeModel && (
          <div className="flex items-center gap-2 mb-4 px-1">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span className="text-xs text-gray-500">
              {activeModel.provider_name} / {activeModel.model_name}
            </span>
            <button onClick={() => setShowProviderModal(true)} className="text-xs text-indigo-600 hover:underline">{t('generate.changeModel')}</button>
          </div>
        )}
        {!activeModel && (
          <div className="flex items-center gap-2 mb-4 px-1">
            <div className="w-2 h-2 rounded-full bg-orange-400 animate-pulse"></div>
            <span className="text-xs text-gray-500">{t('generate.noModel')}</span>
            <button onClick={() => setShowProviderModal(true)} className="text-xs text-indigo-600 hover:underline">{t('generate.configureModel')}</button>
          </div>
        )}
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('generate.difficulty')}</label>
            <CustomSelect
              value={requirements.difficulty}
              onChange={(val) => setRequirements({...requirements, difficulty: val})}
              options={difficultyOptions}
              disabled={generating}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('generate.wordCount')}</label>
            <CustomInput
              value={requirements.word_count}
              onChange={(val) => setRequirements({...requirements, word_count: val})}
              disabled={generating}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('generate.chapterCount')}</label>
            <CustomInput
              value={requirements.chapter_count}
              onChange={(val) => setRequirements({...requirements, chapter_count: val})}
              disabled={generating}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('generate.tags') === 'generate.tags' ? '标签（#标记，如 #小说 #悬疑，留空由 AI 生成）' : t('generate.tags')}
            </label>
            <CustomInput
              value={tagsInput}
              onChange={(val) => setTagsInput(val)}
              disabled={generating}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('generate.card') === 'generate.card' ? '写作卡' : t('generate.card')}
              <a href="/cards" className="ml-2 text-xs text-indigo-600 hover:underline font-normal">
                {t('generate.manageCards') === 'generate.manageCards' ? '管理' : t('generate.manageCards')}
              </a>
            </label>
            {/* 点开弹出卡片选择器，而非下拉列表 */}
            <button
              onClick={() => !generating && setShowCardPicker(true)}
              disabled={generating}
              className="w-full px-3 py-2 text-sm text-left border border-gray-300 rounded-lg bg-white hover:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100 transition-colors flex items-center justify-between disabled:bg-gray-50 disabled:text-gray-400"
            >
              <span className={selectedCard ? 'text-gray-800' : 'text-gray-400'}>
                {selectedCard ? `🃏 ${selectedCard.name}` : (t('generate.noCard') === 'generate.noCard' ? '不使用' : t('generate.noCard'))}
              </span>
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h10" />
              </svg>
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('generate.extraReq') === 'generate.extraReq' ? '额外需求（可选）' : t('generate.extraReq')}
            </label>
            <CustomInput
              value={extraRequirements}
              onChange={(val) => setExtraRequirements(val)}
              disabled={generating}
            />
          </div>
        </div>
        
        <div className="mt-6 flex gap-3">
          <button
            onClick={handleGenerate}
            disabled={generating || !prompt.trim()}
            className="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {generating ? t('generate.generating') : t('generate.start')}
          </button>
          
          {generating && (
            <button
              onClick={handleCancel}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              {t('generate.cancel')}
            </button>
          )}
        </div>
      </div>

      {outline && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">{t('generate.outlinePreview')}</h2>
          <OutlineTree outline={outline} />
        </div>
      )}

      {generating && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">{t('generate.progress')}</h2>
          <ProgressBar current={currentChapter} total={totalChapters} />
          {statusMessage && (
            <p className="text-sm text-gray-600 mt-3 text-center">{statusMessage}</p>
          )}
          {historyId && (
            <p className="text-xs text-gray-400 mt-2 text-center">
              {t('generate.taskRunning').replace('{id}', historyId)}
            </p>
          )}
        </div>
      )}

      {!generating && historyId && statusMessage && !statusMessage.includes(t('generate.error')) && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
          <p className="text-green-700">{statusMessage}</p>
        </div>
      )}

      {!generating && statusMessage && statusMessage.includes(t('generate.error')) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
          <p className="text-red-700">{statusMessage}</p>
        </div>
      )}

      <ProviderModal open={showProviderModal} onClose={() => setShowProviderModal(false)} />

      {/* 写作卡选择弹窗：一堆可视化卡片 */}
      {showCardPicker && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowCardPicker(false)} />
          <div className="relative bg-white rounded-xl shadow-2xl w-[720px] max-w-[94vw] max-h-[80vh] overflow-y-auto p-6">
            <div className="flex items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900 flex-1">
                {t('generate.pickCard') === 'generate.pickCard' ? '选择写作卡' : t('generate.pickCard')}
              </h2>
              <a href="/cards" className="text-xs text-indigo-600 hover:underline mr-4">
                {t('generate.manageCards') === 'generate.manageCards' ? '管理' : t('generate.manageCards')}
              </a>
              <button onClick={() => setShowCardPicker(false)} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {/* 不使用 */}
              <button
                onClick={() => { setCardId(''); setShowCardPicker(false) }}
                className={`h-40 rounded-xl border-2 border-dashed flex flex-col items-center justify-center gap-2 transition-all ${
                  cardId === ''
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-600'
                    : 'border-gray-300 text-gray-400 hover:border-indigo-300 hover:text-indigo-400'
                }`}
              >
                <span className="text-3xl">∅</span>
                <span className="text-sm">{t('generate.noCard') === 'generate.noCard' ? '不使用' : t('generate.noCard')}</span>
              </button>

              {cards.map((c) => (
                <button
                  key={c.id}
                  onClick={() => { setCardId(c.id); setShowCardPicker(false) }}
                  className={`h-40 rounded-xl p-4 text-left flex flex-col shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg ${
                    cardId === c.id
                      ? 'ring-2 ring-indigo-500 bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-300'
                      : 'border border-gray-200 bg-gradient-to-br from-white to-indigo-50/40 hover:border-indigo-300'
                  }`}
                >
                  <div className="flex items-start gap-1.5">
                    <span className="text-lg leading-none">🃏</span>
                    <h3 className="font-semibold text-sm text-gray-800 leading-snug flex-1 line-clamp-2">{c.name}</h3>
                  </div>
                  {(c.tags || []).length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {c.tags.slice(0, 3).map((tag) => (
                        <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-100 text-indigo-700">#{tag}</span>
                      ))}
                    </div>
                  )}
                  {c.extra_requirements && (
                    <p className="text-[11px] text-gray-400 mt-2 line-clamp-2">{c.extra_requirements}</p>
                  )}
                  <div className="flex-1" />
                  {c.builtin && (
                    <span className="self-start text-[10px] px-1.5 py-0.5 rounded bg-purple-100 text-purple-700">
                      {t('cards.builtin') === 'cards.builtin' ? '内置' : t('cards.builtin')}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Generate
