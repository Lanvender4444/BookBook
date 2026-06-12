import { useNavigate } from 'react-router-dom'
import BookCover from './BookCover'

function BookCard({ book, onDelete }) {
  const navigate = useNavigate()

  // 语言代码到显示名称的简单映射
  const langNames = {
    'zh-CN': '简体中文',
    'zh-TW': '繁體中文',
    'en': 'English',
    'ja': '日本語',
    'ko': '한국어',
    'fr': 'Français',
    'es': 'Español',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt-BR': 'Português',
    'ru': 'Русский',
    'ar': 'العربية',
    'hi': 'हिन्दी',
    'th': 'ไทย',
    'vi': 'Tiếng Việt'
  }

  const langLabel = langNames[book.language] || book.language || ''

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
      <div className="h-40 rounded-t-lg overflow-hidden">
        <BookCover book={book} />
      </div>
      
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2 line-clamp-2">{book.title}</h3>
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{book.description}</p>

        {(book.tags || []).length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {book.tags.slice(0, 5).map((tag) => (
              <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-600">#{tag}</span>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
          <span>
            {book.chapter_count ?? book.outline?.chapters?.length ?? 0} 章
            {book.word_count ? ` · ${book.word_count > 10000 ? (book.word_count / 10000).toFixed(1) + '万' : book.word_count}字` : ''}
            {book.created_at ? ` · ${String(book.created_at).slice(0, 10)}` : ''}
          </span>
          <div className="flex gap-1">
            {langLabel && (
              <span className="px-2 py-1 rounded bg-gray-100 text-gray-600">
                {langLabel}
              </span>
            )}
            <span className={`px-2 py-1 rounded ${
              book.source === 'local' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
            }`}>
              {book.source === 'local' ? '本地' : 'P2P'}
            </span>
          </div>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={() => navigate(`/reader/${book.id}`)}
            className="flex-1 bg-indigo-600 text-white py-2 px-3 rounded-md text-sm hover:bg-indigo-700"
          >
            阅读
          </button>
          {book.source === 'local' && (
            <button
              onClick={() => onDelete(book.id)}
              className="px-3 py-2 bg-red-100 text-red-600 rounded-md text-sm hover:bg-red-200"
            >
              删除
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default BookCard
