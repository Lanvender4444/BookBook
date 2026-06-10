import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useI18n } from '../i18n'
import { api } from '../api'
import OutlineTree from '../components/OutlineTree'
import ProgressBar from '../components/ProgressBar'
import CustomSelect from '../components/CustomSelect'
import CustomInput from '../components/CustomInput'
import TypewriterHeading from '../components/TypewriterHeading'
import TypewriterPlaceholder from '../components/TypewriterPlaceholder'

function Generate() {
  const { t, locale } = useI18n()
  const [searchParams] = useSearchParams()
  const [prompt, setPrompt] = useState(searchParams.get('prompt') || '')
  const [requirements, setRequirements] = useState({
    difficulty: searchParams.get('difficulty') || 'medium',
    word_count: searchParams.get('word_count') || '5000',
    chapter_count: searchParams.get('chapter_count') || '5-8',
    style: searchParams.get('style') || ''
  })
  const [outline, setOutline] = useState(null)
  const [chapters, setChapters] = useState([])
  const [generating, setGenerating] = useState(false)
  const [currentChapter, setCurrentChapter] = useState(0)
  const [totalChapters, setTotalChapters] = useState(0)
  const [historyId, setHistoryId] = useState(null)
  const [statusMessage, setStatusMessage] = useState('')
  const [activeModel, setActiveModel] = useState(null)
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
    api.getActiveModel().then(data => {
      if (data.active) setActiveModel(data.active)
    }).catch(() => {})
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
    if (data.book_id) navigate(`/reader/${data.book_id}`)
  }

  const handleErrorEvent = (data) => {
    setGenerating(false)
    generatingRef.current = false
    setStatusMessage(`${t('generate.error')}: ${data.message}`)
  }

  const handleGenerate = async () => {
    if (!prompt.trim() || generatingRef.current) return
    
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
            <a href="/settings" className="text-xs text-indigo-600 hover:underline">{t('generate.changeModel')}</a>
          </div>
        )}
        {!activeModel && (
          <div className="flex items-center gap-2 mb-4 px-1">
            <div className="w-2 h-2 rounded-full bg-orange-400"></div>
            <span className="text-xs text-gray-500">{t('generate.noModel')}</span>
            <a href="/settings" className="text-xs text-indigo-600 hover:underline">{t('generate.configureModel')}</a>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('generate.style')}</label>
            <CustomInput
              value={requirements.style}
              onChange={(val) => setRequirements({...requirements, style: val})}
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
    </div>
  )
}

export default Generate
