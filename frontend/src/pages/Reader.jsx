import { useEffect, useState, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github.css'
import '../styles/typora-reader.css'

function Reader() {
  const { id } = useParams()
  const [book, setBook] = useState(null)
  const [content, setContent] = useState('')
  const [headings, setHeadings] = useState([])
  const [activeId, setActiveId] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    fetchBook()
  }, [id])

  const fetchBook = async () => {
    try {
      const response = await fetch(`/api/books/${id}`)
      const data = await response.json()
      setBook(data)
      
      const exportResponse = await fetch(`/api/books/${id}/export?format=markdown`)
      const exportData = await exportResponse.json()
      setContent(exportData.content)
    } catch (error) {
      console.error('Error fetching book:', error)
    }
  }

  const headingsList = useMemo(() => {
    if (!content) return []
    
    const lines = content.split('\n')
    const result = []
    let inCodeBlock = false
    
    lines.forEach((line, index) => {
      if (line.trim().startsWith('```')) {
        inCodeBlock = !inCodeBlock
        return
      }
      
      if (inCodeBlock) return
      
      const match = line.match(/^(#{1,6})\s+(.+)/)
      if (match) {
        const level = match[1].length
        const text = match[2].trim()
        const id = `heading-${index}`
        result.push({ id, level, text, line: index })
      }
    })
    
    return result
  }, [content])

  useEffect(() => {
    if (headingsList.length === 0) return
    
    const mainContent = document.querySelector('main')
    if (!mainContent) return
    
    let ticking = false
    
    const observer = new IntersectionObserver(
      (entries) => {
        if (!ticking) {
          window.requestAnimationFrame(() => {
            for (const entry of entries) {
              if (entry.isIntersecting) {
                setActiveId(entry.target.id)
                break
              }
            }
            ticking = false
          })
          ticking = true
        }
      },
      { 
        root: mainContent,
        rootMargin: '-15% 0px -75% 0px',
        threshold: 0
      }
    )
    
    const headingElements = headingsList
      .map(({ id }) => document.getElementById(id))
      .filter(Boolean)
    
    headingElements.forEach((el) => observer.observe(el))
    
    return () => {
      headingElements.forEach((el) => observer.unobserve(el))
    }
  }, [headingsList])

  const scrollToHeading = (headingId) => {
    setActiveId(headingId)
    const el = document.getElementById(headingId)
    if (el) {
      const mainEl = document.querySelector('main')
      if (mainEl) {
        const elRect = el.getBoundingClientRect()
        const mainRect = mainEl.getBoundingClientRect()
        const scrollTop = mainEl.scrollTop
        const offsetTop = elRect.top - mainRect.top + scrollTop - 80
        mainEl.scrollTo({ top: offsetTop, behavior: 'smooth' })
      }
    }
  }

  const handleExport = async () => {
    try {
      const response = await fetch(`/api/books/${id}/export?format=markdown`)
      const data = await response.json()
      
      const blob = new Blob([data.content], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${book.title}.md`
      a.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error exporting book:', error)
    }
  }

  const getIndentClass = (level) => {
    const indentMap = {
      1: 'pl-2',
      2: 'pl-6',
      3: 'pl-10',
      4: 'pl-14',
      5: 'pl-18',
      6: 'pl-20'
    }
    return indentMap[level] || 'pl-2'
  }

  const getFontSizeClass = (level) => {
    const sizeMap = {
      1: 'text-sm font-semibold',
      2: 'text-sm font-medium',
      3: 'text-xs',
      4: 'text-xs',
      5: 'text-xs',
      6: 'text-xs'
    }
    return sizeMap[level] || 'text-xs'
  }

  if (!book) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-50">
        <div className="text-gray-500">加载中...</div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-white">
      {/* 左侧目录栏 */}
      <aside className={`${sidebarOpen ? 'w-72' : 'w-0'} bg-gray-50 border-r border-gray-200 transition-all duration-300 overflow-hidden flex flex-col`}>
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-gray-800 truncate">{book.title}</h2>
            <button 
              onClick={() => setSidebarOpen(false)}
              className="text-gray-400 hover:text-gray-600 ml-2 flex-shrink-0"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1 truncate">{book.description}</p>
        </div>
        
        {/* 目录树 */}
        <nav className="flex-1 overflow-y-auto p-3">
          <div className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3 px-2">
            目录
          </div>
          <ul className="space-y-0.5">
            {headingsList.map((heading) => (
              <li key={heading.id}>
                <button
                  onClick={() => scrollToHeading(heading.id)}
                  className={`w-full text-left py-1.5 px-2 rounded transition-colors ${
                    getIndentClass(heading.level)
                  } ${
                    getFontSizeClass(heading.level)
                  } ${
                    activeId === heading.id 
                      ? 'bg-indigo-100 text-indigo-700 border-l-2 border-indigo-500' 
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                  }`}
                  title={heading.text}
                >
                  <span className="truncate block">{heading.text}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>
        
        {/* 底部按钮 */}
        <div className="p-3 border-t border-gray-200">
          <button
            onClick={handleExport}
            className="w-full bg-white border border-gray-300 text-gray-700 py-2 px-4 rounded-lg text-sm hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            导出 Markdown
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 overflow-y-auto">
        {/* 顶部工具栏 */}
        <div className="sticky top-0 bg-white/80 backdrop-blur-sm border-b border-gray-100 z-10">
          <div className="max-w-4xl mx-auto px-8 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {!sidebarOpen && (
                <button 
                  onClick={() => setSidebarOpen(true)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                  </svg>
                </button>
              )}
              <span className="text-sm text-gray-400">
                {headingsList.length > 0 && `${headingsList.length} 个章节`}
              </span>
            </div>
          </div>
        </div>

        {/* 文章内容 */}
        <article className="max-w-4xl mx-auto px-8 py-8 typora-reader">
          <div className="prose prose-lg max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                h1: ({node, ...props}) => {
                  const idx = headingsList.findIndex(h => h.text === props.children?.[0])
                  const headingId = idx >= 0 ? headingsList[idx].id : `h-${Math.random().toString(36).substr(2, 9)}`
                  return <h1 id={headingId} {...props} />
                },
                h2: ({node, ...props}) => {
                  const text = typeof props.children === 'string' ? props.children : 
                               Array.isArray(props.children) ? props.children.join('') : ''
                  const idx = headingsList.findIndex(h => h.text === text)
                  const headingId = idx >= 0 ? headingsList[idx].id : `h-${Math.random().toString(36).substr(2, 9)}`
                  return <h2 id={headingId} {...props} />
                },
                h3: ({node, ...props}) => {
                  const text = typeof props.children === 'string' ? props.children : 
                               Array.isArray(props.children) ? props.children.join('') : ''
                  const idx = headingsList.findIndex(h => h.text === text)
                  const headingId = idx >= 0 ? headingsList[idx].id : `h-${Math.random().toString(36).substr(2, 9)}`
                  return <h3 id={headingId} {...props} />
                },
                code: ({node, inline, className, children, ...props}) => {
                  const match = /language-(\w+)/.exec(className || '')
                  const lang = match ? match[1] : ''
                  
                  if (inline) {
                    return <code className="inline-code" {...props}>{children}</code>
                  }
                  return (
                    <div className="code-block-wrapper">
                      {lang && <div className="code-lang-label">{lang}</div>}
                      <pre className={`language-${lang || 'text'}`}>
                        <code className={`language-${lang || 'text'}`} {...props}>{children}</code>
                      </pre>
                    </div>
                  )
                }
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        </article>
      </main>
    </div>
  )
}

export default Reader
