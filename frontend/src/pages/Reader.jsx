import { useEffect, useState, useMemo, useRef, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { useI18n } from '../i18n'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github.css'
import '../styles/typora-reader.css'

// ✅ Fix 5: 常量提到组件外，避免每次渲染重新创建对象
const INDENT_MAP = {
  1: 'pl-2',
  2: 'pl-6',
  3: 'pl-10',
  4: 'pl-14',
  5: 'pl-18',
  6: 'pl-20'
}

const SIZE_MAP = {
  1: 'text-sm font-semibold',
  2: 'text-sm font-medium',
  3: 'text-xs',
  4: 'text-xs',
  5: 'text-xs',
  6: 'text-xs'
}

const getIndentClass = (level) => INDENT_MAP[level] || 'pl-2'
const getFontSizeClass = (level) => SIZE_MAP[level] || 'text-xs'

// 提取标题文本（统一逻辑，供 h1/h2/h3 共用）
const extractText = (children) => {
  if (typeof children === 'string') return children
  if (Array.isArray(children)) return children.join('')
  return ''
}

function Reader() {
  const { t } = useI18n()
  const { id } = useParams()
  const [book, setBook] = useState(null)
  const [content, setContent] = useState('')
  const [activeId, setActiveId] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [openMenuOpen, setOpenMenuOpen] = useState(false)
  const [exportMenuOpen, setExportMenuOpen] = useState(false)
  const [toast, setToast] = useState({ show: false, message: '', type: 'error' })

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (exportMenuOpen && !e.target.closest('.export-dropdown-container')) {
        setExportMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [exportMenuOpen])

  // ✅ Fix 2: ticking 用 ref 存，避免 observer 重建时状态丢失
  const tickingRef = useRef(false)
  const toastTimer = useRef(null)

  const showToast = useCallback((message, type = 'error') => {
    if (toastTimer.current) {
      clearTimeout(toastTimer.current)
    }
    setToast({ show: true, message, type })
    toastTimer.current = setTimeout(() => {
      setToast({ show: false, message: '', type: 'error' })
    }, 3000)
  }, [])

  // ✅ Fix 4: 两个 fetch 并行执行
  useEffect(() => {
    const fetchBook = async () => {
      try {
        const [bookRes, exportRes] = await Promise.all([
          fetch(`/api/books/${id}`),
          fetch(`/api/books/${id}/export?format=markdown`)
        ])
        const [data, exportData] = await Promise.all([
          bookRes.json(),
          exportRes.json()
        ])
        setBook(data)
        setContent(exportData.content)
      } catch (error) {
        console.error('Error fetching book:', error)
      }
    }

    fetchBook()
  }, [id])

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
        const headingId = `heading-${index}`
        result.push({ id: headingId, level, text, line: index })
      }
    })

    return result
  }, [content])

  // ✅ Fix 1: O(1) 查找，避免 O(n²) 的 findIndex
  const headingMap = useMemo(() => {
    const map = new Map()
    headingsList.forEach((h) => map.set(h.text, h.id))
    return map
  }, [headingsList])

  useEffect(() => {
    if (headingsList.length === 0) return

    const mainContent = document.querySelector('main')
    if (!mainContent) return

    const observer = new IntersectionObserver(
      (entries) => {
        // ✅ Fix 2: 使用 ref 存 ticking，不受 observer 重建影响
        if (!tickingRef.current) {
          tickingRef.current = true
          window.requestAnimationFrame(() => {
            for (const entry of entries) {
              if (entry.isIntersecting) {
                setActiveId(entry.target.id)
                break
              }
            }
            tickingRef.current = false
          })
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
      observer.disconnect()
    }
  }, [headingsList])

  const scrollToHeading = useCallback((headingId) => {
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
  }, [])

  const EXPORT_FORMATS = [
    { value: 'markdown', label: 'Markdown (.md)', mime: 'text/markdown', ext: 'md' },
    { value: 'txt', label: '纯文本 (.txt)', mime: 'text/plain', ext: 'txt' },
    { value: 'epub', label: 'EPUB 电子书 (.epub)', mime: 'application/epub+zip', ext: 'epub' },
    { value: 'docx', label: 'Word 文档 (.docx)', mime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', ext: 'docx' },
    { value: 'pdf', label: 'PDF (.pdf)', mime: 'application/pdf', ext: 'pdf' },
  ]

  const handleExport = useCallback(async (format = 'markdown') => {
    try {
      const fmt = EXPORT_FORMATS.find(f => f.value === format) || EXPORT_FORMATS[0]

      if (format === 'markdown') {
        const response = await fetch(`/api/books/${id}/export?format=markdown`)
        const data = await response.json()
        const blob = new Blob([data.content], { type: 'text/markdown' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${book.title}.${fmt.ext}`
        a.click()
        URL.revokeObjectURL(url)
      } else {
        const response = await fetch(`/api/books/${id}/export?format=${format}`)
        if (!response.ok) {
          const errData = await response.json().catch(() => ({}))
          showToast(errData.detail || '导出失败', 'error')
          return
        }
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${book.title}.${fmt.ext}`
        a.click()
        URL.revokeObjectURL(url)
      }
      showToast('导出成功', 'success')
    } catch (error) {
      console.error('Error exporting book:', error)
      showToast('导出失败', 'error')
    }
    setExportMenuOpen(false)
  }, [id, book, showToast])

  const handleOpenBook = useCallback(async (app) => {
    try {
      const url = app
        ? `/api/books/${id}/open?app=${encodeURIComponent(app)}`
        : `/api/books/${id}/open`
      const response = await fetch(url, { method: 'POST' })
      const data = await response.json()
      if (!response.ok) {
        showToast('打开失败: ' + (data.detail || data.message), 'error')
      } else {
        showToast('已尝试用应用打开', 'success')
      }
    } catch (error) {
      console.error('Error opening book:', error)
      showToast('打开失败', 'error')
    }
    setOpenMenuOpen(false)
  }, [id, showToast])

  const handleCustomOpen = useCallback(() => {
    const app = window.prompt('请输入应用路径（如 C:\\Program Files\\Typora\\Typora.exe）：')
    if (app) {
      handleOpenBook(app)
    } else {
      setOpenMenuOpen(false)
    }
  }, [handleOpenBook])

  // ✅ Fix 1 & 3: 统一文本提取，用 Map O(1) 查找，不再用 Math.random()
  const makeHeadingComponent = useCallback(
    (Tag) =>
      ({ node, children, ...props }) => {
        const text = extractText(children)
        const headingId = headingMap.get(text)
        // 找不到时用稳定的文本派生 ID，不用随机数
        const stableId = headingId ?? `h-${text.replace(/\s+/g, '-').toLowerCase().slice(0, 32)}`
        return (
          <Tag id={stableId} {...props}>
            {children}
          </Tag>
        )
      },
    [headingMap]
  )

  const markdownComponents = useMemo(
    () => ({
      h1: makeHeadingComponent('h1'),
      h2: makeHeadingComponent('h2'),
      h3: makeHeadingComponent('h3'),
      code: ({ node, inline, className, children, ...props }) => {
        const match = /language-(\w+)/.exec(className || '')
        const lang = match ? match[1] : ''

        if (inline) {
          return <code className="inline-code" {...props}>{children}</code>
        }
        return (
          <div className="code-block-wrapper">
            {lang && <div className="code-lang-label">{lang}</div>}
            <pre className={`language-${lang || 'text'}`}>
              <code className={`language-${lang || 'text'}`} {...props}>
                {children}
              </code>
            </pre>
          </div>
        )
      }
    }),
    [makeHeadingComponent]
  )

  if (!book) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-50">
        <div className="text-gray-500">加载中...</div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-white">
      {/* Toast 通知 */}
      {toast.show && (
        <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-lg shadow-lg text-sm transition-opacity ${
          toast.type === 'success'
            ? 'bg-green-600 text-white'
            : 'bg-red-600 text-white'
        }`}>
          {toast.message}
        </div>
      )}
      {/* 左侧目录栏 */}
      <aside
        className={`${
          sidebarOpen ? 'w-72' : 'w-0'
        } bg-gray-50 border-r border-gray-200 transition-all duration-300 overflow-hidden flex flex-col`}
      >
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
          {book.language && (
            <div className="mt-2">
              <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                {book.language}
              </span>
            </div>
          )}
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
                  className={`w-full text-left py-1.5 px-2 rounded transition-colors ${getIndentClass(
                    heading.level
                  )} ${getFontSizeClass(heading.level)} ${
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
        <div className="p-3 border-t border-gray-200 space-y-2">
          <div className="relative export-dropdown-container">
            <button
              onClick={() => setExportMenuOpen(!exportMenuOpen)}
              className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg text-sm hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              导出
              <svg className={`w-3 h-3 transition-transform ${exportMenuOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {exportMenuOpen && (
              <div className="absolute bottom-full left-0 right-0 mb-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-20">
                {EXPORT_FORMATS.map((fmt) => (
                  <button
                    key={fmt.value}
                    onClick={() => handleExport(fmt.value)}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                  >
                    {fmt.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="relative">
            <button
              onClick={() => setOpenMenuOpen(!openMenuOpen)}
              className="w-full bg-white border border-gray-300 text-gray-700 py-2 px-4 rounded-lg text-sm hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              用其他应用打开
            </button>
            {openMenuOpen && (
              <div className="absolute bottom-full left-0 right-0 mb-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-20">
                <button
                  onClick={() => handleOpenBook()}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  系统默认应用
                </button>
                <button
                  onClick={() => handleOpenBook('Typora')}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Typora
                </button>
                <button
                  onClick={handleCustomOpen}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  其他应用...
                </button>
              </div>
            )}
          </div>
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
              components={markdownComponents}
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