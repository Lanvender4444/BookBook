import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import OutlineTree from '../components/OutlineTree'
import ProgressBar from '../components/ProgressBar'

function Generate() {
  const [prompt, setPrompt] = useState('')
  const [requirements, setRequirements] = useState({
    difficulty: '中等',
    word_count: '5000',
    chapter_count: '5-8',
    style: '科普向'
  })
  const [outline, setOutline] = useState(null)
  const [chapters, setChapters] = useState([])
  const [generating, setGenerating] = useState(false)
  const [currentChapter, setCurrentChapter] = useState(0)
  const [totalChapters, setTotalChapters] = useState(0)
  const navigate = useNavigate()

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    
    setGenerating(true)
    setOutline(null)
    setChapters([])
    
    try {
      const response = await fetch('/api/generate/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, requirements })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'outline') {
                setOutline(data.data)
                setTotalChapters(data.data.chapters.length)
              } else if (data.type === 'chapter') {
                setChapters(prev => [...prev, data.data])
                setCurrentChapter(data.index + 1)
              } else if (data.type === 'done') {
                setGenerating(false)
                navigate(`/reader/${data.book_id}`)
              }
            } catch (e) {}
          }
        }
      }
    } catch (error) {
      console.error('Generation error:', error)
      setGenerating(false)
    }
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
        />
        
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">难易度</label>
            <select
              value={requirements.difficulty}
              onChange={(e) => setRequirements({...requirements, difficulty: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
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
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">章节数量</label>
            <input
              type="text"
              value={requirements.chapter_count}
              onChange={(e) => setRequirements({...requirements, chapter_count: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">风格</label>
            <input
              type="text"
              value={requirements.style}
              onChange={(e) => setRequirements({...requirements, style: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>
        
        <button
          onClick={handleGenerate}
          disabled={generating || !prompt.trim()}
          className="mt-6 w-full bg-indigo-600 text-white py-3 px-4 rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {generating ? '生成中...' : '开始生成'}
        </button>
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
        </div>
      )}
    </div>
  )
}

export default Generate
