import { useEffect, useState } from 'react'
import BookCard from '../components/BookCard'

function Library() {
  const [books, setBooks] = useState([])
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchBooks()
  }, [])

  const fetchBooks = async () => {
    try {
      const response = await fetch('/api/books')
      const data = await response.json()
      setBooks(data)
    } catch (error) {
      console.error('Error fetching books:', error)
    }
  }

  const handleDelete = async (bookId) => {
    if (confirm('确定要删除这本书吗？')) {
      try {
        await fetch(`/api/books/${bookId}`, { method: 'DELETE' })
        fetchBooks()
      } catch (error) {
        console.error('Error deleting book:', error)
      }
    }
  }

  const filteredBooks = books.filter(book => {
    if (filter === 'all') return true
    return book.source === filter
  })

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">我的书库</h1>
      
      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-md ${filter === 'all' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          全部
        </button>
        <button
          onClick={() => setFilter('local')}
          className={`px-4 py-2 rounded-md ${filter === 'local' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          本地
        </button>
        <button
          onClick={() => setFilter('p2p')}
          className={`px-4 py-2 rounded-md ${filter === 'p2p' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          P2P 来源
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredBooks.map(book => (
          <BookCard key={book.id} book={book} onDelete={handleDelete} />
        ))}
      </div>

      {filteredBooks.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          暂无书籍，去生成一本吧！
        </div>
      )}
    </div>
  )
}

export default Library
