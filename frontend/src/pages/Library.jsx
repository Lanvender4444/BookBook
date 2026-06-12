import { useEffect, useState, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useI18n } from '../i18n'
import BookCard from '../components/BookCard'
import ConfirmModal from '../components/ConfirmModal'
import CustomInput from '../components/CustomInput'

const FALLBACK = {
  'library.search': '搜索书名 / 标签 / 简介…',
  'library.allTags': '全部标签',
  'library.allLangs': '全部语言',
  'library.dateFrom': '从',
  'library.dateTo': '到',
  'library.viewGrid': '卡片视图',
  'library.viewShelf': '书架模式',
  'library.words': '字',
  'library.chapters': '章',
  'library.createdAt': '创建于',
  'library.clearFilters': '清除筛选',
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

  return (
    <div className="relative group self-end" style={{ width: w, height: h }}>
      <button
        onClick={() => onOpen(book.id)}
        className="w-full h-full rounded-t-sm shadow-[2px_0_4px_rgba(0,0,0,0.35)] transition-transform duration-150 group-hover:-translate-y-3 cursor-pointer overflow-hidden"
        style={{
          background: `linear-gradient(90deg, ${c2} 0%, ${c1} 18%, ${c1} 82%, ${c2} 100%)`,
          borderLeft: '1px solid rgba(255,255,255,0.18)',
          borderRight: '1px solid rgba(0,0,0,0.35)',
        }}
      >
        {/* 书脊上下装饰线 */}
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

      {/* 悬停资料卡 */}
      <div className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-4 w-64 opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-30">
        <div className="bg-gray-900/95 text-white rounded-lg shadow-xl p-3 text-xs space-y-1.5">
          <p className="font-semibold text-sm leading-snug">{book.title}</p>
          {book.description && <p className="text-gray-300 line-clamp-3">{book.description}</p>}
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
        <div className="w-2.5 h-2.5 bg-gray-900/95 rotate-45 mx-auto -mt-1.5" />
      </div>
    </div>
  )
}

function BookShelf({ books, langName }) {
  const navigate = useNavigate()
  // 按厚度装箱：每层书架放约 900px 宽
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
          {/* 隔板 */}
          <div
            className="h-4 rounded-sm shadow-md mb-1"
            style={{ background: 'linear-gradient(180deg, #8a5a2b 0%, #6b4423 55%, #4a2e16 100%)' }}
          />
        </div>
      ))}
    </div>
  )
}

function Library() {
  const { t } = useI18n()
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
  const [tagFilter, setTagFilter] = useState('')
  const [langFilter, setLangFilter] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [view, setView] = useState('grid') // grid | shelf

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

  const handleDelete = (bookId) => {
    setDeleteModal({ open: true, bookId })
  }

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

  const filteredBooks = books.filter((book) => {
    if (filter !== 'all' && book.source !== filter) return false
    if (tagFilter && !(book.tags || []).includes(tagFilter)) return false
    if (langFilter && book.language !== langFilter) return false
    if (query) {
      const q = query.toLowerCase()
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

  const hasFilters = query || tagFilter || langFilter || dateFrom || dateTo

  const filterOptions = [
    { key: 'all', label: t('library.all') },
    { key: 'local', label: t('library.local') },
    { key: 'p2p', label: t('library.p2p') }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{t('library.title')}</h1>
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

      {/* 搜索与筛选栏 */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 space-y-3">
        <div className="flex gap-2 flex-wrap items-center">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={tt('library.search')}
            className="flex-1 min-w-[220px] px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
          />
          <select
            value={langFilter}
            onChange={(e) => setLangFilter(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white"
          >
            <option value="">{tt('library.allLangs')}</option>
            {allLangs.map((l) => (
              <option key={l} value={l}>{langName(l)}</option>
            ))}
          </select>
          <div className="flex items-center gap-1.5 text-sm text-gray-500">
            <span>{tt('library.dateFrom')}</span>
            <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)}
              className="px-2 py-1.5 text-sm border border-gray-300 rounded-lg" />
            <span>{tt('library.dateTo')}</span>
            <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)}
              className="px-2 py-1.5 text-sm border border-gray-300 rounded-lg" />
          </div>
          {hasFilters && (
            <button
              onClick={() => { setQuery(''); setTagFilter(''); setLangFilter(''); setDateFrom(''); setDateTo('') }}
              className="text-xs text-indigo-600 hover:underline"
            >
              {tt('library.clearFilters')}
            </button>
          )}
        </div>

        {allTags.length > 0 && (
          <div className="flex gap-1.5 flex-wrap">
            <button
              onClick={() => setTagFilter('')}
              className={`px-2.5 py-1 text-xs rounded-full transition-colors ${
                tagFilter === '' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {tt('library.allTags')}
            </button>
            {allTags.map((tag) => (
              <button
                key={tag}
                onClick={() => setTagFilter(tagFilter === tag ? '' : tag)}
                className={`px-2.5 py-1 text-xs rounded-full transition-colors ${
                  tagFilter === tag ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                #{tag}
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

        {/* 视图切换：卡片 / 模拟真实书架 */}
        <div className="flex rounded-lg border border-gray-200 overflow-hidden">
          <button
            onClick={() => setView('grid')}
            className={`px-4 py-2 text-sm transition-colors ${
              view === 'grid' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            {tt('library.viewGrid')}
          </button>
          <button
            onClick={() => setView('shelf')}
            className={`px-4 py-2 text-sm transition-colors ${
              view === 'shelf' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            📚 {tt('library.viewShelf')}
          </button>
        </div>
      </div>

      {view === 'shelf' ? (
        filteredBooks.length > 0 && <BookShelf books={filteredBooks} langName={langName} />
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
