import { useEffect, useState } from 'react'
import BookCard from '../components/BookCard'

function Library() {
  const [books, setBooks] = useState([])
  const [filter, setFilter] = useState('all')
  const [booksDir, setBooksDir] = useState('')
  const [newDir, setNewDir] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [userInfo, setUserInfo] = useState(null)

  useEffect(() => {
    fetchBooks()
    fetchBooksDir()
    fetchUserInfo()
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
        alert('保存地址已更新')
      }
    } catch (error) {
      console.error('Error updating dir:', error)
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
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">我的书库</h1>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="text-gray-600 hover:text-indigo-600 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          设置
        </button>
      </div>

      {showSettings && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">设置</h2>
          
          {userInfo && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-700 mb-2">用户信息</h3>
              <p className="text-sm text-gray-600">
                <span className="font-medium">用户 ID：</span>
                <code className="ml-2 px-2 py-1 bg-gray-200 rounded text-xs">{userInfo.user_id}</code>
              </p>
            </div>
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              书籍保存位置
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={newDir}
                onChange={(e) => setNewDir(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="例如: C:\Users\YourName\BookBook"
              />
              <button
                onClick={handleUpdateDir}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                保存
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              当前位置: {booksDir}
            </p>
          </div>
        </div>
      )}

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
