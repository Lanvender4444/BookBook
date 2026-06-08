import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Generate from './pages/Generate'
import Library from './pages/Library'
import Reader from './pages/Reader'
import Network from './pages/Network'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <img src="/icon.png" alt="Logo" className="h-8 w-8 mr-2" />
                <span className="text-xl font-bold text-indigo-600">AI eBook Generator</span>
              </div>
              <div className="flex items-center space-x-4">
                <a href="/generate" className="text-gray-700 hover:text-indigo-600">生成</a>
                <a href="/library" className="text-gray-700 hover:text-indigo-600">书库</a>
                <a href="/network" className="text-gray-700 hover:text-indigo-600">网络</a>
              </div>
            </div>
          </div>
        </nav>
        
        <Routes>
          <Route path="/" element={<Generate />} />
          <Route path="/generate" element={<Generate />} />
          <Route path="/library" element={<Library />} />
          <Route path="/reader/:id" element={<Reader />} />
          <Route path="/network" element={<Network />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
