import { useNavigate } from 'react-router-dom'

function BookCard({ book, onDelete }) {
  const navigate = useNavigate()

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
      <div className="h-40 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-t-lg flex items-center justify-center">
        <span className="text-white text-4xl">📖</span>
      </div>
      
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2 line-clamp-2">{book.title}</h3>
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{book.description}</p>
        
        <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
          <span>{book.outline?.chapters?.length || 0} 章</span>
          <span className={`px-2 py-1 rounded ${
            book.source === 'local' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
          }`}>
            {book.source === 'local' ? '本地' : 'P2P'}
          </span>
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
