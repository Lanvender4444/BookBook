import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import OutlineTree from '../components/OutlineTree'
import ProgressBar from '../components/ProgressBar'

const LANGUAGES = {
  "zh-CN": "中文（简体）",
  "zh-TW": "中文（繁體）",
  "en": "English",
  "ja": "日本語",
  "ko": "한국어",
  "es": "español",
  "fr": "français",
  "de": "Deutsch",
  "it": "italiano",
  "pt-BR": "português (Brasil)",
  "ru": "русский",
  "ar": "العربية",
  "hi": "हिन्दी",
  "th": "ไทย",
  "vi": "Tiếng Việt",
  "id": "Indonesia",
  "ms": "Melayu",
  "tr": "Türkçe",
  "pl": "polski",
  "nl": "Nederlands",
  "sv": "svenska",
  "da": "dansk",
  "fi": "suomi",
  "nb": "norsk bokmål",
  "cs": "čeština",
  "sk": "slovenčina",
  "hu": "magyar",
  "ro": "română",
  "bg": "български",
  "uk": "українська",
  "el": "Ελληνικά",
  "he": "עברית",
  "bn": "বাংলা",
  "ta": "தமிழ்",
  "te": "తెలుగు",
  "ml": "മലയാളം",
  "kn": "ಕನ್ನಡ",
  "ca": "català",
  "hr": "hrvatski",
  "sl": "slovenščina",
  "et": "eesti",
  "lv": "latviešu",
  "lt": "lietuvių",
  "fil": "Filipino",
  "sw": "Kiswahili",
  "af": "Afrikaans"
}

function Generate() {
  const [searchParams] = useSearchParams()
  const [prompt, setPrompt] = useState(searchParams.get('prompt') || '')
  const [requirements, setRequirements] = useState({
    difficulty: searchParams.get('difficulty') || '中等',
    word_count: searchParams.get('word_count') || '5000',
    chapter_count: searchParams.get('chapter_count') || '5-8',
    style: searchParams.get('style') || '科普向',
    language: searchParams.get('language') || 'zh-CN'
  })
  const [outline, setOutline] = useState(null)
  const [chapters, setChapters] = useState([])
  const [generating, setGenerating] = useState(false)
  const [currentChapter, setCurrentChapter] = useState(0)
  const [totalChapters, setTotalChapters] = useState(0)
  const [historyId, setHistoryId] = useState(null)
  const [statusMessage, setStatusMessage] = useState('')
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
    setStatusMessage('正在重新连接...')
    
    try {
      const response = await fetch(`/api/generate/stream/${taskId}`, {
        signal
      })
      
      await processSSEStream(response, signal)
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Reconnect error:', error)
        setStatusMessage('重新连接失败')
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
          } catch (e) {
          }
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
          if (prev.some(c => c.index === data.current_chapter - 1)) {
            return prev
          }
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
    setStatusMessage('生成完成！')
    
    if (data.book_id) {
      navigate(`/reader/${data.book_id}`)
    }
  }

  const handleErrorEvent = (data) => {
    console.error('Generation error:', data.message)
    setGenerating(false)
    generatingRef.current = false
    setStatusMessage(`错误: ${data.message}`)
  }

  const handleGenerate = async () => {
    if (!prompt.trim() || generatingRef.current) return
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    
    abortControllerRef.current = new AbortController()
    const signal = abortControllerRef.current.signal
    
    setGenerating(true)
    generatingRef.current = true
    setOutline(null)
    setChapters([])
    setCurrentChapter(0)
    setTotalChapters(0)
    setHistoryId(null)
    setStatusMessage('准备开始...')
    
    try {
      const response = await fetch('/api/generate/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, requirements }),
        signal
      })

      await processSSEStream(response, signal)
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Generation error:', error)
      }
      if (isMountedRef.current) {
        setGenerating(false)
        generatingRef.current = false
      }
    }
  }

  const handleCancel = async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    
    if (historyId) {
      try {
        await fetch(`/api/generate/${historyId}/cancel`, { method: 'POST' })
      } catch (e) {
        console.error('Cancel error:', e)
      }
    }
    
    setGenerating(false)
    generatingRef.current = false
    setStatusMessage('已取消')
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">生成电子书</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          描述你想生成的书籍
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder="例如：一本关于人工智能入门的书籍，适合初学者阅读..."
          disabled={generating}
        />
        
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">难易度</label>
            <select
              value={requirements.difficulty}
              onChange={(e) => setRequirements({...requirements, difficulty: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              disabled={generating}
            >
              <option>简单</option>
              <option>中等</option>
              <option>困难</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">目标字数</label>
            <input
              type="text"
              value={requirements.word_count}
              onChange={(e) => setRequirements({...requirements, word_count: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              disabled={generating}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">章节数量</label>
            <input
              type="text"
              value={requirements.chapter_count}
              onChange={(e) => setRequirements({...requirements, chapter_count: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              disabled={generating}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">风格</label>
            <input
              type="text"
              value={requirements.style}
              onChange={(e) => setRequirements({...requirements, style: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              disabled={generating}
            />
          </div>
          
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">生成语言</label>
            <select
              value={requirements.language}
              onChange={(e) => setRequirements({...requirements, language: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              disabled={generating}
            >
              {Object.entries(LANGUAGES).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="mt-6 flex gap-3">
          <button
            onClick={handleGenerate}
            disabled={generating || !prompt.trim()}
            className="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? '生成中...' : '开始生成'}
          </button>
          
          {generating && (
            <button
              onClick={handleCancel}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
            >
              取消
            </button>
          )}
        </div>
      </div>

      {outline && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">大纲预览</h2>
          <OutlineTree outline={outline} />
        </div>
      )}

      {generating && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">生成进度</h2>
          <ProgressBar current={currentChapter} total={totalChapters} />
          {statusMessage && (
            <p className="text-sm text-gray-600 mt-3 text-center">{statusMessage}</p>
          )}
          {historyId && (
            <p className="text-xs text-gray-400 mt-2 text-center">
              任务 #{historyId} · 切换页面不会中断生成
            </p>
          )}
        </div>
      )}

      {!generating && historyId && statusMessage && !statusMessage.includes('错误') && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
          <p className="text-green-700">{statusMessage}</p>
        </div>
      )}

      {!generating && statusMessage && statusMessage.includes('错误') && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
          <p className="text-red-700">{statusMessage}</p>
        </div>
      )}
    </div>
  )
}

export default Generate
