import { useEffect, useState, useCallback, useMemo, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useI18n } from '../i18n'
import BookCard from '../components/BookCard'
import BookCover from '../components/BookCover'
import ConfirmModal from '../components/ConfirmModal'
import CustomInput from '../components/CustomInput'
import TypewriterHeading from '../components/TypewriterHeading'

// 标题打字机速度：CJK 慢一点更自然
const titleSpeed = (locale) => (['zh-CN', 'zh-TW', 'ja', 'ko'].includes(locale) ? 200 : 120)

const FALLBACK = {
  'library.search': '搜索书名 / 标签 / 语言…',
  'library.tagsBtn': '标签',
  'library.langsBtn': '语言',
  'library.allLangs': '全部语言',
  'library.selectAll': '全选',
  'library.clearSel': '清除',
  'library.dateFrom': '从',
  'library.dateTo': '到',
  'library.viewGrid': '卡片视图',
  'library.viewName': '名称视图',
  'library.viewCover': '平铺视图',
  'library.viewShelf': '书架模式',
  'library.clearFilters': '清除筛选',
  'library.tagPickTitle': '选择标签',
  'library.tagSearchPh': '搜索标签…',
  'library.noTagMatch': '没有匹配的标签',
  'library.sugTitle': '书名',
  'library.sugTag': '标签',
  'library.sugLang': '语言',
  'library.done': '完成',
}

// 书脊配色（按书名哈希取色，同一本书颜色稳定）
const SPINE_COLORS = [
  ['#7c3aed', '#5b21b6'], ['#2563eb', '#1e40af'], ['#0d9488', '#115e59'],
  ['#dc2626', '#991b1b'], ['#d97706', '#92400e'], ['#4f46e5', '#3730a3'],
  ['#be185d', '#831843'], ['#059669', '#065f46'], ['#7f1d1d', '#450a0a'],
  ['#1e3a8a', '#172554'], ['#713f12', '#422006'], ['#374151', '#1f2937'],
]

function hashStr(s) {
  let h = 0
  for (let i = 0; i < (s || '').length; i++) h = (h * 31 + s.charCodeAt(i)) | 0
  return Math.abs(h)
}

// 字数 → 书脊厚度（px），有上限
function spineWidth(wordCount) {
  const MIN = 26, MAX = 64, CAP = 300000
  if (!wordCount) return 34
  return Math.round(MIN + (Math.min(wordCount, CAP) / CAP) * (MAX - MIN))
}

function spineHeight(title) {
  return 150 + (hashStr(title) % 4) * 10 // 150~180px，错落有致
}

function fmtWords(n) {
  if (!n) return '—'
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : String(n)
}

function BookSpine({ book, onOpen, langLabel }) {
  const [c1, c2] = SPINE_COLORS[hashStr(book.title) % SPINE_COLORS.length]
  const w = spineWidth(book.word_count)
  const h = spineHeight(book.title)
  // 根据书在视口中的位置决定信息卡对齐方式，避免被屏幕边缘遮挡
  const [tipAlign, setTipAlign] = useState('center') // left | center | right
  const TIP_W = 256

  const handleEnter = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const center = rect.left + rect.width / 2
    if (center - TIP_W / 2 < 12) setTipAlign('left')
    else if (center + TIP_W / 2 > window.innerWidth - 12) setTipAlign('right')
    else setTipAlign('center')
  }

  const tipPos =
    tipAlign === 'left'
      ? 'left-0'
      : tipAlign === 'right'
        ? 'right-0'
        : 'left-1/2 -translate-x-1/2'
  const arrowPos =
    tipAlign === 'left' ? 'ml-3' : tipAlign === 'right' ? 'mr-3 ml-auto' : 'mx-auto'

  return (
    <div className="relative group self-end" style={{ width: w, height: h }} onMouseEnter={handleEnter}>
      <button
        onClick={() => onOpen(book.id)}
        className="w-full h-full rounded-t-sm shadow-[2px_0_4px_rgba(0,0,0,0.35)] transition-transform duration-150 group-hover:-translate-y-3 cursor-pointer overflow-hidden"
        style={{
          background: `linear-gradient(90deg, ${c2} 0%, ${c1} 18%, ${c1} 82%, ${c2} 100%)`,
          borderLeft: '1px solid rgba(255,255,255,0.18)',
          borderRight: '1px solid rgba(0,0,0,0.35)',
        }}
      >
        <div className="absolute top-2 left-1 right-1 h-px bg-white/30" />
        <div className="absolute bottom-2 left-1 right-1 h-px bg-white/30" />
        <span
          className="absolute inset-0 flex items-center justify-center text-white/95 font-medium px-0.5"
          style={{
            writingMode: 'vertical-rl',
            fontSize: w >= 40 ? 12 : 11,
            lineHeight: 1.1,
            maxHeight: h - 24,
            overflow: 'hidden',
            textShadow: '0 1px 2px rgba(0,0,0,0.5)',
          }}
        >
          {book.title?.slice(0, 18)}
        </span>
      </button>

      {/* 悬停资料卡（按位置自适应对齐），带书封面 */}
      <div className={`pointer-events-none absolute bottom-full ${tipPos} mb-4 w-64 opacity-0 translate-y-1 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-200 z-30`}>
        <div className="bg-gray-900/95 text-white rounded-lg shadow-xl p-3 text-xs space-y-1.5">
          <div className="flex gap-2.5">
            <div className="w-16 flex-shrink-0 aspect-[3/4] rounded overflow-hidden shadow-md">
              <BookCover book={book} rounded="rounded" />
            </div>
            <div className="min-w-0 flex-1 space-y-1">
              <p className="font-semibold text-sm leading-snug line-clamp-3">{book.title}</p>
              {book.description && <p className="text-gray-300 line-clamp-3">{book.description}</p>}
            </div>
          </div>
          <div className="flex flex-wrap gap-1">
            {(book.tags || []).slice(0, 6).map((tag) => (
              <span key={tag} className="px-1.5 py-0.5 rounded-full bg-white/15">#{tag}</span>
            ))}
          </div>
          <p className="text-gray-400">
            {fmtWords(book.word_count)} 字 · {book.chapter_count || 0} 章{langLabel ? ` · ${langLabel}` : ''}
          </p>
          {book.created_at && (
            <p className="text-gray-400">{String(book.created_at).slice(0, 10)}</p>
          )}
        </div>
        <div className={`w-2.5 h-2.5 bg-gray-900/95 rotate-45 -mt-1.5 ${arrowPos}`} />
      </div>
    </div>
  )
}

function BookShelf({ books, langName }) {
  const navigate = useNavigate()
  const shelves = useMemo(() => {
    const rows = []
    let row = [], width = 0
    for (const b of books) {
      const w = spineWidth(b.word_count) + 6
      if (width + w > 880 && row.length) {
        rows.push(row)
        row = []
        width = 0
      }
      row.push(b)
      width += w
    }
    if (row.length) rows.push(row)
    return rows
  }, [books])

  return (
    <div
      className="rounded-xl p-6 pb-2 shadow-inner"
      style={{ background: 'linear-gradient(180deg, #3f2a1a 0%, #54381f 100%)' }}
    >
      {shelves.map((row, i) => (
        <div key={i}>
          <div className="flex items-end gap-1.5 px-3 min-h-[190px] pt-8">
            {row.map((book) => (
              <BookSpine
                key={book.id}
                book={book}
                langLabel={langName(book.language)}
                onOpen={(id) => navigate(`/reader/${id}`)}
              />
            ))}
          </div>
          <div
            className="h-4 rounded-sm shadow-md mb-1"
            style={{ background: 'linear-gradient(180deg, #8a5a2b 0%, #6b4423 55%, #4a2e16 100%)' }}
          />
        </div>
      ))}
    </div>
  )
}

// 名称视图：只显示书名的紧凑列表
function BookNameList({ books }) {
  const navigate = useNavigate()
  return (
    <div className="bg-white rounded-lg shadow divide-y divide-gray-100 overflow-hidden">
      {books.map((book) => {
        const [c1] = SPINE_COLORS[hashStr(book.title) % SPINE_COLORS.length]
        return (
          <button
            key={book.id}
            onClick={() => navigate(`/reader/${book.id}`)}
            className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-indigo-50/60 transition-colors"
          >
            <span className="w-1.5 h-5 rounded-full flex-shrink-0" style={{ background: c1 }} />
            <span className="flex-1 min-w-0 truncate text-gray-800 font-medium">{book.title}</span>
            {book.word_count ? (
              <span className="text-xs text-gray-400 flex-shrink-0">{fmtWords(book.word_count)} 字</span>
            ) : null}
          </button>
        )
      })}
    </div>
  )
}

// 平铺视图：只显示书封面，悬停浮现书名
function BookCoverWall({ books }) {
  const navigate = useNavigate()
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      {books.map((book) => (
        <button
          key={book.id}
          onClick={() => navigate(`/reader/${book.id}`)}
          className="group relative aspect-[3/4] rounded-lg overflow-hidden shadow hover:shadow-xl transition-all hover:-translate-y-1"
          title={book.title}
        >
          <BookCover book={book} rounded="rounded-lg" />
          <div className="absolute inset-x-0 bottom-0 p-2 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
            <span className="text-white text-xs font-medium line-clamp-2 text-left block">{book.title}</span>
          </div>
        </button>
      ))}
    </div>
  )
}

function Library() {
  const { t, locale } = useI18n()
  const tt = useCallback((key) => {
    const v = t(key)
    return v === key ? (FALLBACK[key] ?? key) : v
  }, [t])

  const [books, setBooks] = useState([])
  const [filter, setFilter] = useState('all')
  const [booksDir, setBooksDir] = useState('')
  const [newDir, setNewDir] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [userInfo, setUserInfo] = useState(null)
  const [deleteModal, setDeleteModal] = useState({ open: false, bookId: null })

  // 搜索与筛选
  const [query, setQuery] = useState('')
  const [showSuggest, setShowSuggest] = useState(false)
  const [selectedTags, setSelectedTags] = useState([])     // 多选标签（弹窗选择）
  const [selectedLangs, setSelectedLangs] = useState([])   // 多选语言（复选框）；空 = 全部
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [view, setView] = useState('grid') // grid | shelf

  // 标签弹窗 / 语言下拉
  const [showTagModal, setShowTagModal] = useState(false)
  const [tagSearch, setTagSearch] = useState('')
  const [showLangMenu, setShowLangMenu] = useState(false)
  const langMenuRef = useRef(null)
  const searchBoxRef = useRef(null)

  const langNames = {
    'zh-CN': '简体中文', 'zh-TW': '繁體中文', 'en': 'English', 'ja': '日本語',
    'ko': '한국어', 'fr': 'Français', 'es': 'Español', 'de': 'Deutsch',
    'it': 'Italiano', 'pt-BR': 'Português', 'ru': 'Русский', 'ar': 'العربية',
    'hi': 'हिन्दी', 'th': 'ไทย', 'vi': 'Tiếng Việt',
  }
  const langName = (code) => langNames[code] || code || ''

  useEffect(() => {
    fetchBooks()
    fetchBooksDir()
    fetchUserInfo()
  }, [])

  // 点击外部关闭语言下拉 / 搜索建议
  useEffect(() => {
    const onDown = (e) => {
      if (langMenuRef.current && !langMenuRef.current.contains(e.target)) setShowLangMenu(false)
      if (searchBoxRef.current && !searchBoxRef.current.contains(e.target)) setShowSuggest(false)
    }
    document.addEventListener('mousedown', onDown)
    return () => document.removeEventListener('mousedown', onDown)
  }, [])

  const fetchBooks = async () => {
    try {
      const response = await fetch('/api/books')
      const data = await response.json()
      setBooks(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching books:', error)
    }
  }

  const fetchBooksDir = async () => {
    try {
      const response = await fetch('/api/books/config/dir')
      const data = await response.json()
      setBooksDir(data.dir)
      setNewDir(data.dir)
    } catch (error) {
      console.error('Error fetching books dir:', error)
    }
  }

  const fetchUserInfo = async () => {
    try {
      const response = await fetch('/api/identity')
      const data = await response.json()
      setUserInfo(data)
    } catch (error) {
      console.error('Error fetching user info:', error)
    }
  }

  const handleUpdateDir = async () => {
    try {
      const response = await fetch('/api/books/config/dir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: newDir })
      })
      if (response.ok) {
        setBooksDir(newDir)
        setShowSettings(false)
        alert(t('library.saved'))
      }
    } catch (error) {
      console.error('Error updating dir:', error)
    }
  }

  const handleDelete = (bookId) => setDeleteModal({ open: true, bookId })

  const confirmDelete = async () => {
    try {
      await fetch(`/api/books/${deleteModal.bookId}`, { method: 'DELETE' })
      fetchBooks()
    } catch (error) {
      console.error('Error deleting book:', error)
    }
    setDeleteModal({ open: false, bookId: null })
  }

  const allTags = useMemo(() => [...new Set(books.flatMap((b) => b.tags || []))], [books])
  const allLangs = useMemo(() => [...new Set(books.map((b) => b.language).filter(Boolean))], [books])

  const toggleTag = (tag) =>
    setSelectedTags((prev) => (prev.includes(tag) ? prev.filter((x) => x !== tag) : [...prev, tag]))
  const toggleLang = (l) =>
    setSelectedLangs((prev) => (prev.includes(l) ? prev.filter((x) => x !== l) : [...prev, l]))

  // 分类搜索建议：书名 / 标签 / 语言
  const suggestions = useMemo(() => {
    const q = query.trim().toLowerCase().replace(/^#/, '')
    if (!q) return null
    return {
      titles: books.filter((b) => (b.title || '').toLowerCase().includes(q)).slice(0, 5),
      tags: allTags.filter((tag) => tag.toLowerCase().includes(q) && !selectedTags.includes(tag)).slice(0, 8),
      langs: allLangs.filter((l) => (langName(l).toLowerCase().includes(q) || l.toLowerCase().includes(q)) && !selectedLangs.includes(l)).slice(0, 5),
    }
  }, [query, books, allTags, allLangs, selectedTags, selectedLangs])

  const filteredBooks = books.filter((book) => {
    if (filter !== 'all' && book.source !== filter) return false
    if (selectedTags.length > 0 && !selectedTags.some((tag) => (book.tags || []).includes(tag))) return false
    if (selectedLangs.length > 0 && !selectedLangs.includes(book.language)) return false
    if (query) {
      const q = query.toLowerCase().replace(/^#/, '')
      const inTitle = (book.title || '').toLowerCase().includes(q)
      const inDesc = (book.description || '').toLowerCase().includes(q)
      const inTags = (book.tags || []).some((tag) => tag.toLowerCase().includes(q))
      const inLang = langName(book.language).toLowerCase().includes(q)
      if (!inTitle && !inDesc && !inTags && !inLang) return false
    }
    if (dateFrom || dateTo) {
      const created = book.created_at ? String(book.created_at).slice(0, 10) : ''
      if (!created) return false
      if (dateFrom && created < dateFrom) return false
      if (dateTo && created > dateTo) return false
    }
    return true
  })

  const hasFilters = query || selectedTags.length || selectedLangs.length || dateFrom || dateTo
  const clearAll = () => { setQuery(''); setSelectedTags([]); setSelectedLangs([]); setDateFrom(''); setDateTo('') }

  const filterOptions = [
    { key: 'all', label: t('library.all') },
    { key: 'local', label: t('library.local') },
    { key: 'p2p', label: t('library.p2p') }
  ]

  const filteredTagOptions = allTags.filter((tag) => tag.toLowerCase().includes(tagSearch.trim().toLowerCase().replace(/^#/, '')))

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <TypewriterHeading text={t('library.title')} speed={titleSpeed(locale)} fontSize="1.875rem" className="text-gray-900" />
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="text-gray-600 hover:text-indigo-600 flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {t('library.settings')}
        </button>
      </div>

      {showSettings && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">{t('library.settings')}</h2>

          {userInfo && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-700 mb-2">{t('library.userInfo')}</h3>
              <p className="text-sm text-gray-600">
                <span className="font-medium">{t('library.userId')}：</span>
                <code className="ml-2 px-2 py-1 bg-gray-200 rounded text-xs">{userInfo.user_id}</code>
              </p>
            </div>
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('library.booksDir')}
            </label>
            <div className="flex gap-2">
              <div className="flex-1">
                <CustomInput
                  value={newDir}
                  onChange={setNewDir}
                  placeholder="C:\Users\YourName\BookBook"
                />
              </div>
              <button
                onClick={handleUpdateDir}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                {t('library.save')}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {t('library.currentDir')}: {booksDir}
            </p>
          </div>
        </div>
      )}

      {/* 搜索与筛选栏（各控件定宽，互不挤压） */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 space-y-3">
        <div className="flex gap-2 flex-wrap items-center">
          {/* 搜索框 + 分类建议 */}
          <div ref={searchBoxRef} className="relative flex-1 min-w-[240px]">
            <input
              type="text"
              value={query}
              onChange={(e) => { setQuery(e.target.value); setShowSuggest(true) }}
              onFocus={() => setShowSuggest(true)}
              placeholder={tt('library.search')}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
            />
            {showSuggest && suggestions && (suggestions.titles.length || suggestions.tags.length || suggestions.langs.length) > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-40 overflow-hidden max-h-80 overflow-y-auto animate-dropdown">
                {suggestions.tags.length > 0 && (
                  <div className="p-2 border-b border-gray-100">
                    <p className="text-[10px] text-gray-400 uppercase mb-1 px-1">{tt('library.sugTag')}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {suggestions.tags.map((tag) => (
                        <button key={tag}
                          onClick={() => { toggleTag(tag); setQuery(''); setShowSuggest(false) }}
                          className="px-2.5 py-1 text-xs rounded-full bg-indigo-50 text-indigo-700 hover:bg-indigo-100">
                          #{tag}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {suggestions.langs.length > 0 && (
                  <div className="p-2 border-b border-gray-100">
                    <p className="text-[10px] text-gray-400 uppercase mb-1 px-1">{tt('library.sugLang')}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {suggestions.langs.map((l) => (
                        <button key={l}
                          onClick={() => { toggleLang(l); setQuery(''); setShowSuggest(false) }}
                          className="px-2.5 py-1 text-xs rounded-full bg-emerald-50 text-emerald-700 hover:bg-emerald-100">
                          {langName(l)}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {suggestions.titles.length > 0 && (
                  <div className="p-2">
                    <p className="text-[10px] text-gray-400 uppercase mb-1 px-1">{tt('library.sugTitle')}</p>
                    {suggestions.titles.map((b) => (
                      <button key={b.id}
                        onClick={() => { setQuery(b.title); setShowSuggest(false) }}
                        className="block w-full text-left px-2 py-1.5 text-sm text-gray-700 hover:bg-gray-50 rounded truncate">
                        📖 {b.title}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* 标签按钮 → 弹窗（定宽） */}
          <button
            onClick={() => { setShowTagModal(true); setTagSearch('') }}
            className={`w-28 shrink-0 px-3 py-2 text-sm border rounded-lg transition-colors text-center ${
              selectedTags.length ? 'border-indigo-400 bg-indigo-50 text-indigo-700' : 'border-gray-300 bg-white text-gray-600 hover:border-indigo-300'
            }`}
          >
            # {tt('library.tagsBtn')}{selectedTags.length ? ` (${selectedTags.length})` : ''}
          </button>

          {/* 语言复选下拉（定宽） */}
          <div ref={langMenuRef} className="relative shrink-0">
            <button
              onClick={() => setShowLangMenu(!showLangMenu)}
              className={`w-36 px-3 py-2 text-sm border rounded-lg transition-colors text-center ${
                selectedLangs.length ? 'border-emerald-400 bg-emerald-50 text-emerald-700' : 'border-gray-300 bg-white text-gray-600 hover:border-emerald-300'
              }`}
            >
              🌐 {selectedLangs.length ? `${tt('library.langsBtn')} (${selectedLangs.length})` : tt('library.allLangs')}
            </button>
            {showLangMenu && (
              <div className="absolute top-full right-0 mt-1 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-40 p-2 animate-dropdown">
                <div className="flex gap-2 px-1 pb-2 border-b border-gray-100 mb-1">
                  <button onClick={() => setSelectedLangs([...allLangs])} className="text-xs text-indigo-600 hover:underline">{tt('library.selectAll')}</button>
                  <button onClick={() => setSelectedLangs([])} className="text-xs text-gray-500 hover:underline">{tt('library.clearSel')}</button>
                </div>
                <div className="max-h-56 overflow-y-auto">
                  {allLangs.map((l) => (
                    <label key={l} className="flex items-center gap-2 px-1.5 py-1.5 text-sm text-gray-700 hover:bg-gray-50 rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedLangs.includes(l)}
                        onChange={() => toggleLang(l)}
                        className="accent-indigo-600"
                      />
                      {langName(l)}
                    </label>
                  ))}
                  {allLangs.length === 0 && <p className="text-xs text-gray-400 px-1.5 py-2">—</p>}
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center gap-1.5 text-sm text-gray-500 shrink-0">
            <span>{tt('library.dateFrom')}</span>
            <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)}
              className="px-2 py-1.5 text-sm border border-gray-300 rounded-lg w-[140px]" />
            <span>{tt('library.dateTo')}</span>
            <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)}
              className="px-2 py-1.5 text-sm border border-gray-300 rounded-lg w-[140px]" />
          </div>

          {hasFilters && (
            <button onClick={clearAll} className="text-xs text-indigo-600 hover:underline shrink-0">
              {tt('library.clearFilters')}
            </button>
          )}
        </div>

        {/* 只展示已选中的标签 */}
        {selectedTags.length > 0 && (
          <div className="flex gap-1.5 flex-wrap">
            {selectedTags.map((tag) => (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className="px-2.5 py-1 text-xs rounded-full bg-indigo-600 text-white hover:bg-indigo-700"
                title="点击移除"
              >
                #{tag} ×
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-between items-center mb-6 flex-wrap gap-2">
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

        <div className="flex rounded-lg border border-gray-200 overflow-hidden">
          {[
            { key: 'grid', label: tt('library.viewGrid') },
            { key: 'name', label: tt('library.viewName') },
            { key: 'cover', label: tt('library.viewCover') },
            { key: 'shelf', label: tt('library.viewShelf') },
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setView(key)}
              className={`px-4 py-2 text-sm transition-colors ${
                view === key ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {view === 'shelf' ? (
        filteredBooks.length > 0 && <BookShelf books={filteredBooks} langName={langName} />
      ) : view === 'name' ? (
        <BookNameList books={filteredBooks} />
      ) : view === 'cover' ? (
        <BookCoverWall books={filteredBooks} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBooks.map(book => (
            <BookCard key={book.id} book={book} onDelete={handleDelete} />
          ))}
        </div>
      )}

      {filteredBooks.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          {t('library.noBooks')}
        </div>
      )}

      {/* 标签选择弹窗：搜索 + 多选 */}
      {showTagModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40 animate-overlay" onClick={() => setShowTagModal(false)} />
          <div className="relative bg-white rounded-xl shadow-2xl w-[520px] max-w-[92vw] max-h-[70vh] flex flex-col p-5 animate-modal">
            <div className="flex items-center mb-3">
              <h2 className="text-lg font-semibold text-gray-900 flex-1">{tt('library.tagPickTitle')}</h2>
              <button onClick={() => setShowTagModal(false)} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
            </div>
            <input
              type="text"
              value={tagSearch}
              onChange={(e) => setTagSearch(e.target.value)}
              placeholder={tt('library.tagSearchPh')}
              autoFocus
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
            />
            <div className="flex-1 overflow-y-auto">
              <div className="flex flex-wrap gap-2">
                {filteredTagOptions.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => toggleTag(tag)}
                    className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                      selectedTags.includes(tag)
                        ? 'bg-indigo-600 text-white border-indigo-600'
                        : 'bg-white text-gray-600 border-gray-300 hover:border-indigo-400'
                    }`}
                  >
                    #{tag}
                  </button>
                ))}
                {filteredTagOptions.length === 0 && (
                  <p className="text-sm text-gray-400 py-6 w-full text-center">{tt('library.noTagMatch')}</p>
                )}
              </div>
            </div>
            <div className="flex justify-between items-center border-t pt-3 mt-3">
              <button onClick={() => setSelectedTags([])} className="text-xs text-gray-500 hover:underline">
                {tt('library.clearSel')}
              </button>
              <button
                onClick={() => setShowTagModal(false)}
                className="px-4 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                {tt('library.done')}{selectedTags.length ? ` (${selectedTags.length})` : ''}
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={deleteModal.open}
        title={t('library.confirmDeleteTitle')}
        message={t('library.confirmDelete')}
        confirmText={t('modal.confirm')}
        cancelText={t('modal.cancel')}
        danger={true}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteModal({ open: false, bookId: null })}
      />
    </div>
  )
}

export default Library
