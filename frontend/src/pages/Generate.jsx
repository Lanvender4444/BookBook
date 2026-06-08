import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import OutlineTree from '../components/OutlineTree'
import ProgressBar from '../components/ProgressBar'

function Generate() {
  const [searchParams] = useSearchParams()
  const [prompt, setPrompt] = useState(searchParams.get('prompt') || '')
  const [requirements, setRequirements] = useState({
    difficulty: searchParams.get('difficulty') || '中等',
    word_count: searchParams.get('word_count') || '5000',
    chapter_count: searchParams.get('chapter_count') || '5-8',
    style: searchParams.get('style') || '科普向'
  })
  const [outline, setOutline] = useState(null)
  const [chapters, setChapters] = useState([])
  const [generating, setGenerating] = useState(false)
  const [currentChapter, setCurrentChapter] = useState(0)
  const [totalChapters, setTotalChapters] = useState(0)
  const [historyId, setHistoryId] = useState(null)
  const navigate = useNavigate()
  
  // 使用 ref 存储 abort controller 和组件是否挂载
  const abortControllerRef = useRef(null)
  const isMountedRef = useRef(true)
  const generatingRef = useRef(false)

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      isMountedRef.current = false
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  const handleGenerate = async () => {
    if (!prompt.trim() || generatingRef.current) return
    
    // 如果有之前的请求，先取消
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    
    // 创建新的 abort controller
    abortControllerRef.current = new AbortController()
    const signal = abortControllerRef.current.signal
    
    setGenerating(true)
    generatingRef.current = true
    setOutline(null)
    setChapters([])
    setCurrentChapter(0)
    setTotalChapters(0)
    setHistoryId(null)
    
    try {
      const response = await fetch('/api/generate/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, requirements }),
        signal
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        // 检查是否已取消
        if (signal.aborted) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6).trim()
              const data = JSON.parse(jsonStr)
              
              // 处理 history_id 事件
              if (data.history_id) {
                setHistoryId(data.history_id)
              } else if (data.type === 'outline') {
                setOutline(data.data)
                setTotalChapters(data.data.chapters.length)
              } else if (data.type === 'chapter') {
                setChapters(prev => [...prev, data.data])
                setCurrentChapter(data.index + 1)
              } else if (data.type === 'done') {
                setGenerating(false)
                generatingRef.current = false
                navigate(`/reader/${data.book_id}`)
              } else if (data.type === 'error') {
                console.error('Generation error:', data.message)
                setGenerating(false)
                generatingRef.current = false
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
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
    // 取消前端请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    
    // 通知后端取消
    if (historyId) {
      try {
        await fetch(`/api/generate/${historyId}/cancel`, { method: 'POST' })
      } catch (e) {
        console.error('Cancel error:', e)
      }
    }
    
    setGenerating(false)
    generatingRef.current = false
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
          {historyId && (
            <p className="text-xs text-gray-400 mt-2 text-center">
              任务 #{historyId} · 切换页面不会中断生成
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default Generate
