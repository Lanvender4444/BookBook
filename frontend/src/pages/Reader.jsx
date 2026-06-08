import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'

function Reader() {
  const { id } = useParams()
  const [book, setBook] = useState(null)
  const [chapters, setChapters] = useState([])
  const [currentChapter, setCurrentChapter] = useState(0)

  useEffect(() => {
    fetchBook()
  }, [id])

  const fetchBook = async () => {
    try {
      const response = await fetch(`/api/books/${id}`)
      const data = await response.json()
      setBook(data)
      
      const chaptersResponse = await fetch(`/api/books/${id}/chapters`)
      const chaptersData = await chaptersResponse.json()
      setChapters(chaptersData)
    } catch (error) {
      console.error('Error fetching book:', error)
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

  if (!book) {
    return <div className="flex justify-center items-center h-screen">加载中...</div>
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-white shadow-lg overflow-y-auto">
        <div className="p-4 border-b">
          <h2 className="font-bold text-lg">{book.title}</h2>
          <p className="text-sm text-gray-600 mt-1">{book.description}</p>
        </div>
        
        <nav className="p-4">
          <ul className="space-y-2">
            {chapters.map((chapter, index) => (
              <li key={index}>
                <button
                  onClick={() => setCurrentChapter(index)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm ${
                    currentChapter === index ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-gray-100'
                  }`}
                >
                  {index + 1}. {chapter.title}
                </button>
              </li>
            ))}
          </ul>
        </nav>
        
        <div className="p-4 border-t">
          <button
            onClick={handleExport}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700"
          >
            导出 Markdown
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <article className="max-w-3xl mx-auto p-8">
          {chapters[currentChapter] && (
            <>
              <h1 className="text-3xl font-bold mb-4">{chapters[currentChapter].title}</h1>
              <div className="prose prose-lg max-w-none">
                <ReactMarkdown>{chapters[currentChapter].content}</ReactMarkdown>
              </div>
            </>
          )}
        </article>
      </main>
    </div>
  )
}

export default Reader
